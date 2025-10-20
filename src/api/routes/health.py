"""
Health check and system status routes.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import time
import sys
import socket
import os

from ..models import HealthResponse, HealthCheckResult, ConfigResponse
from config.policy_loader import load_config
from monitoring.prometheus_metrics import get_metrics_collector

router = APIRouter(prefix="/api/v1", tags=["health"])

# Track server start time
_server_start_time = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Get system health status.
    
    Returns:
        Health status with component checks
    """
    try:
        config = load_config()
        uptime = time.time() - _server_start_time
        
        checks = []
        components = {
            "api": "healthy",
            "config": "healthy"
        }
        
        # Check Docker connectivity
        try:
            from inventory.docker_scanner import DockerScanner
            check_start = time.time()
            scanner = DockerScanner(
                socket_path=config.docker.socket_path,
                state_manager=None
            )
            scanner.close()
            duration = (time.time() - check_start) * 1000
            
            checks.append(HealthCheckResult(
                check_type="docker",
                status="healthy",
                message="Docker daemon accessible",
                duration_ms=duration,
                timestamp=datetime.utcnow()
            ))
            components["docker"] = "healthy"
        except Exception as e:
            checks.append(HealthCheckResult(
                check_type="docker",
                status="unhealthy",
                message=str(e),
                duration_ms=0,
                timestamp=datetime.utcnow()
            ))
            components["docker"] = "unhealthy"
        
        # Check Kubernetes connectivity
        try:
            from inventory.k8s_scanner import KubernetesScanner
            check_start = time.time()
            k8s_scanner = KubernetesScanner(
                kubeconfig_path=config.kubernetes.kubeconfig_path,
                in_cluster=config.kubernetes.in_cluster,
                namespace=config.kubernetes.namespace,
                state_manager=None
            )
            duration = (time.time() - check_start) * 1000
            
            checks.append(HealthCheckResult(
                check_type="kubernetes",
                status="healthy",
                message="Kubernetes API accessible",
                duration_ms=duration,
                timestamp=datetime.utcnow()
            ))
            components["kubernetes"] = "healthy"
        except Exception as e:
            checks.append(HealthCheckResult(
                check_type="kubernetes",
                status="unhealthy",
                message=str(e),
                duration_ms=0,
                timestamp=datetime.utcnow()
            ))
            components["kubernetes"] = "unhealthy"
        
        # Overall status
        overall_status = "healthy" if all(
            c.status == "healthy" for c in checks
        ) else "degraded"
        
        # Get version from package
        version = os.getenv("SAFE_UPDATER_VERSION", "0.1.0")
        
        return HealthResponse(
            status=overall_status,
            version=version,
            uptime_seconds=uptime,
            checks=checks,
            components=components
        )
    except Exception as e:
        metrics = get_metrics_collector()
        metrics.record_error("api_health", type(e).__name__)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config", response_model=ConfigResponse)
async def get_config():
    """
    Get current configuration.
    
    Returns:
        Current system configuration
    """
    try:
        config = load_config()
        
        return ConfigResponse(
            auto_update_enabled=config.auto_update.update_policy.enabled,
            max_concurrent_updates=config.auto_update.update_policy.max_concurrent,
            semver_gates={
                "patch": config.auto_update.semver_gates.patch.value,
                "minor": config.auto_update.semver_gates.minor.value,
                "major": config.auto_update.semver_gates.major.value,
                "prerelease": config.auto_update.semver_gates.prerelease.value
            },
            rollback_enabled=config.auto_update.rollback.auto_rollback,
            monitoring_enabled=config.monitoring.prometheus_enabled,
            docker_enabled=True,  # Always enabled if configured
            kubernetes_enabled=True  # Always enabled if configured
        )
    except Exception as e:
        metrics = get_metrics_collector()
        metrics.record_error("api_health", type(e).__name__)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/version")
async def get_version():
    """
    Get API version information.
    
    Returns:
        Version details
    """
    return {
        "version": os.getenv("SAFE_UPDATER_VERSION", "0.1.0"),
        "api_version": "v1",
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "hostname": socket.gethostname()
    }
