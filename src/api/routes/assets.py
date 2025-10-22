"""
Asset management routes.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime

from ..models import (
    AssetListResponse,
    AssetResponse,
    AssetStatsResponse,
    AssetType,
    AssetStatus
)
from inventory.state_manager import StateManager
from monitoring.prometheus_metrics import get_metrics_collector

router = APIRouter(prefix="/api/v1/assets", tags=["assets"])


@router.get("/", response_model=AssetListResponse)
async def list_assets(
    asset_type: Optional[AssetType] = None,
    namespace: Optional[str] = None,
    status: Optional[AssetStatus] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100)
):
    """
    List all tracked assets with optional filtering.
    
    Args:
        asset_type: Filter by asset type
        namespace: Filter by namespace
        status: Filter by status
        page: Page number (starts at 1)
        page_size: Number of items per page
    
    Returns:
        Paginated list of assets
    """
    try:
        state_manager = StateManager()
        assets = state_manager.list_assets()
        
        # Apply filters
        if asset_type:
            assets = [a for a in assets if a.asset_type.value == asset_type.value]
        if namespace:
            assets = [a for a in assets if a.namespace == namespace]
        if status:
            assets = [a for a in assets if a.status.value == status.value]
        
        # Pagination
        total = len(assets)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_assets = assets[start:end]
        
        # Convert to response models
        asset_responses = [
            AssetResponse(
                id=asset.id,
                name=asset.name,
                asset_type=AssetType(asset.asset_type.value),
                namespace=asset.namespace,
                current_version=asset.current_version,
                latest_version=asset.latest_version,
                status=AssetStatus(asset.status.value),
                labels=asset.labels,
                created_at=asset.created_at,
                updated_at=asset.updated_at,
                metadata=asset.metadata
            )
            for asset in paginated_assets
        ]
        
        return AssetListResponse(
            assets=asset_responses,
            total=total,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        metrics = get_metrics_collector()
        metrics.record_error("api_assets", type(e).__name__)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=AssetStatsResponse)
async def get_asset_stats():
    """
    Get asset statistics.
    
    Returns:
        Asset statistics grouped by type, status, and namespace
    """
    try:
        state_manager = StateManager()
        stats = state_manager.get_statistics()
        
        return AssetStatsResponse(
            total_assets=stats['total_assets'],
            by_type=stats.get('by_type', {}),
            by_status=stats.get('by_status', {}),
            by_namespace=stats.get('by_namespace', {})
        )
    except Exception as e:
        metrics = get_metrics_collector()
        metrics.record_error("api_assets", type(e).__name__)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(asset_id: str):
    """
    Get details of a specific asset.
    
    Args:
        asset_id: Asset identifier
    
    Returns:
        Asset details
    """
    try:
        state_manager = StateManager()
        asset = state_manager.get_asset(asset_id)
        
        if not asset:
            raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
        
        return AssetResponse(
            id=asset.id,
            name=asset.name,
            asset_type=AssetType(asset.asset_type.value),
            namespace=asset.namespace,
            current_version=asset.current_version,
            latest_version=asset.latest_version,
            status=AssetStatus(asset.status.value),
            labels=asset.labels,
            created_at=asset.created_at,
            updated_at=asset.updated_at,
            metadata=asset.metadata
        )
    except HTTPException:
        raise
    except Exception as e:
        metrics = get_metrics_collector()
        metrics.record_error("api_assets", type(e).__name__)
        raise HTTPException(status_code=500, detail=str(e))
