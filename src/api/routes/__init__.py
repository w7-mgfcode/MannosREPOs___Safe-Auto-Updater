"""
Routes package for REST API.
"""

from .assets import router as assets_router
from .updates import router as updates_router
from .health import router as health_router
from .metrics import router as metrics_router

__all__ = [
    'assets_router',
    'updates_router', 
    'health_router',
    'metrics_router'
]
