"""
FastAPI server for Safe Auto-Updater REST API.
"""

import sys
import socket
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import time

from .routes import (
    assets_router,
    updates_router,
    health_router,
    metrics_router
)
from monitoring.prometheus_metrics import init_metrics_collector, get_metrics_collector
from config.policy_loader import load_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("Starting Safe Auto-Updater API Server...")
    
    # Initialize metrics collector
    metrics = init_metrics_collector()
    
    # Set system info
    version = os.getenv("SAFE_UPDATER_VERSION", "0.1.0")
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    hostname = socket.gethostname()
    
    metrics.set_system_info(
        version=version,
        python_version=python_version,
        hostname=hostname
    )
    
    print(f"✓ Metrics collector initialized")
    print(f"✓ System: {hostname} | Python: {python_version} | Version: {version}")
    
    yield
    
    # Shutdown
    print("Shutting down Safe Auto-Updater API Server...")


def create_app(config_path: Optional[str] = None) -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Args:
        config_path: Path to configuration file
    
    Returns:
        Configured FastAPI application
    """
    # Load configuration
    config = load_config(config_path)
    
    # Create app
    app = FastAPI(
        title="Safe Auto-Updater API",
        description="REST API for Safe Auto-Updater container update management",
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: Make configurable
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Request timing middleware
    @app.middleware("http")
    async def add_metrics_middleware(request: Request, call_next):
        """Add metrics collection to all requests."""
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        metrics = get_metrics_collector()
        metrics.record_api_request(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
            duration=duration
        )
        
        # Add response headers
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        
        return response
    
    # Exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler."""
        metrics = get_metrics_collector()
        metrics.record_error("api_server", type(exc).__name__)
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc),
                "path": request.url.path
            }
        )
    
    # Include routers
    app.include_router(assets_router)
    app.include_router(updates_router)
    app.include_router(health_router)
    app.include_router(metrics_router)
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "service": "Safe Auto-Updater API",
            "version": "0.1.0",
            "status": "running",
            "docs": "/api/docs",
            "health": "/api/v1/health",
            "metrics": "/api/v1/metrics"
        }
    
    return app


def start_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    config_path: Optional[str] = None,
    reload: bool = False,
    workers: int = 1
):
    """
    Start the FastAPI server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
        config_path: Path to configuration file
        reload: Enable auto-reload for development
        workers: Number of worker processes
    """
    app = create_app(config_path)
    
    print(f"\n{'='*60}")
    print(f"Safe Auto-Updater API Server")
    print(f"{'='*60}")
    print(f"Host:     {host}:{port}")
    print(f"Docs:     http://{host}:{port}/api/docs")
    print(f"Health:   http://{host}:{port}/api/v1/health")
    print(f"Metrics:  http://{host}:{port}/api/v1/metrics")
    print(f"Workers:  {workers}")
    print(f"Reload:   {reload}")
    print(f"{'='*60}\n")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        workers=workers,
        log_level="info"
    )


if __name__ == "__main__":
    # Development server
    start_server(reload=True)
