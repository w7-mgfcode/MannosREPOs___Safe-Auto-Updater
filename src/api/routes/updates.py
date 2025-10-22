"""
Update management routes.
"""

from typing import List
from fastapi import APIRouter, HTTPException
from datetime import datetime

from ..models import (
    UpdateEvaluationRequest,
    UpdateEvaluationResponse,
    UpdateRequest,
    UpdateResponse,
    UpdateHistoryResponse,
    ScanRequest,
    ScanResponse,
    VersionChangeType,
    UpdateDecision
)
from detection.diff_gate import DiffGate
from detection.semver_analyzer import SemVerAnalyzer
from inventory.state_manager import StateManager
from inventory.docker_scanner import DockerScanner
from inventory.k8s_scanner import KubernetesScanner
from config.policy_loader import load_config
from monitoring.prometheus_metrics import get_metrics_collector
import time

router = APIRouter(prefix="/api/v1/updates", tags=["updates"])


@router.post("/evaluate", response_model=UpdateEvaluationResponse)
async def evaluate_update(request: UpdateEvaluationRequest):
    """
    Evaluate whether an update should be applied.
    
    Args:
        request: Update evaluation parameters
    
    Returns:
        Evaluation decision and reasoning
    """
    try:
        config = load_config()
        diff_gate = DiffGate(semver_gates=config.auto_update.semver_gates)
        
        result = diff_gate.evaluate_update(
            request.current_version,
            request.new_version
        )
        
        # Record metrics
        metrics = get_metrics_collector()
        metrics.record_update_evaluation(
            change_type=result['change_type'],
            decision=result['decision']
        )
        
        return UpdateEvaluationResponse(
            current_version=request.current_version,
            new_version=request.new_version,
            change_type=VersionChangeType(result['change_type']),
            decision=UpdateDecision(result['decision']),
            safe=result['safe'],
            reason=result['reason'],
            metadata=result
        )
    except Exception as e:
        metrics = get_metrics_collector()
        metrics.record_error("api_updates", type(e).__name__)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scan", response_model=ScanResponse)
async def scan_assets(request: ScanRequest):
    """
    Trigger asset scanning.
    
    Args:
        request: Scan configuration
    
    Returns:
        Scan results
    """
    start_time = time.time()
    docker_count = 0
    k8s_count = 0
    
    try:
        config = load_config()
        state_manager = StateManager()
        metrics = get_metrics_collector()
        
        # Scan Docker
        if request.docker:
            scan_start = metrics.record_scan_start("docker")
            try:
                scanner = DockerScanner(
                    socket_path=config.docker.socket_path,
                    state_manager=state_manager
                )
                docker_assets = scanner.scan_containers(include_stopped=False)
                docker_count = len(docker_assets)
                scanner.close()
                
                metrics.record_scan_complete(
                    "docker",
                    scan_start,
                    "success",
                    docker_count
                )
            except Exception as e:
                metrics.record_scan_complete("docker", scan_start, "failed", 0)
                raise
        
        # Scan Kubernetes
        if request.kubernetes:
            scan_start = metrics.record_scan_start("kubernetes")
            try:
                k8s_scanner = KubernetesScanner(
                    kubeconfig_path=config.kubernetes.kubeconfig_path,
                    in_cluster=config.kubernetes.in_cluster,
                    namespace=request.namespace or "default",
                    state_manager=state_manager
                )
                k8s_assets = k8s_scanner.scan_all_resources()
                k8s_count = len(k8s_assets)
                
                metrics.record_scan_complete(
                    "kubernetes",
                    scan_start,
                    "success",
                    k8s_count
                )
            except Exception as e:
                metrics.record_scan_complete("kubernetes", scan_start, "failed", 0)
                raise
        
        duration = time.time() - start_time
        
        return ScanResponse(
            status="success",
            assets_discovered=docker_count + k8s_count,
            docker_assets=docker_count,
            kubernetes_assets=k8s_count,
            duration_seconds=duration,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        metrics = get_metrics_collector()
        metrics.record_error("api_updates", type(e).__name__)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/apply", response_model=UpdateResponse)
async def apply_update(request: UpdateRequest):
    """
    Apply an update to an asset.
    
    Args:
        request: Update request parameters
    
    Returns:
        Update execution result
    """
    try:
        state_manager = StateManager()
        asset = state_manager.get_asset(request.asset_id)
        
        if not asset:
            raise HTTPException(
                status_code=404,
                detail=f"Asset {request.asset_id} not found"
            )
        
        metrics = get_metrics_collector()
        start_time = metrics.record_update_start(asset.asset_type.value)
        
        # TODO: Implement actual update logic with Helm/Watchtower
        # This is a placeholder for the update implementation
        
        if request.dry_run:
            status = "dry_run_success"
            message = "Dry run completed successfully"
        else:
            status = "pending"
            message = "Update queued for execution"
        
        metrics.record_update_complete(
            asset.asset_type.value,
            start_time,
            status
        )
        
        return UpdateResponse(
            asset_id=request.asset_id,
            status=status,
            previous_version=asset.current_version,
            new_version=request.target_version,
            started_at=datetime.utcnow(),
            message=message,
            rollback_available=True
        )
    except HTTPException:
        raise
    except Exception as e:
        metrics = get_metrics_collector()
        metrics.record_error("api_updates", type(e).__name__)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=List[UpdateHistoryResponse])
async def get_update_history(
    asset_id: str = None,
    limit: int = 50
):
    """
    Get update history.
    
    Args:
        asset_id: Filter by asset ID (optional)
        limit: Maximum number of records
    
    Returns:
        List of update history entries
    """
    try:
        # TODO: Implement update history tracking
        # This is a placeholder
        return []
    except Exception as e:
        metrics = get_metrics_collector()
        metrics.record_error("api_updates", type(e).__name__)
        raise HTTPException(status_code=500, detail=str(e))
