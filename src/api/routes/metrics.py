"""
Metrics endpoint for Prometheus.
"""

from fastapi import APIRouter, Response
from monitoring.prometheus_metrics import get_metrics_collector

router = APIRouter(prefix="/api/v1", tags=["metrics"])


@router.get("/metrics")
async def get_metrics():
    """
    Get Prometheus metrics.
    
    Returns:
        Prometheus metrics in text format
    """
    metrics = get_metrics_collector()
    
    return Response(
        content=metrics.generate_metrics(),
        media_type=metrics.get_content_type()
    )
