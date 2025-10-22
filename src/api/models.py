"""
API request and response models.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class AssetType(str, Enum):
    """Asset type enumeration."""
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    HELM = "helm"


class AssetStatus(str, Enum):
    """Asset status enumeration."""
    ACTIVE = "active"
    PENDING_UPDATE = "pending_update"
    UPDATING = "updating"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class VersionChangeType(str, Enum):
    """Version change type."""
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    PRERELEASE = "prerelease"
    BUILD = "build"
    NO_CHANGE = "no_change"


class UpdateDecision(str, Enum):
    """Update decision."""
    APPROVE = "approve"
    REVIEW_REQUIRED = "review_required"
    MANUAL_APPROVAL = "manual_approval"
    REJECT = "reject"


# ===== ASSET MODELS =====

class AssetResponse(BaseModel):
    """Asset information response."""
    id: str
    name: str
    asset_type: AssetType
    namespace: Optional[str] = None
    current_version: str
    latest_version: Optional[str] = None
    status: AssetStatus
    labels: Dict[str, str] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AssetListResponse(BaseModel):
    """List of assets response."""
    assets: List[AssetResponse]
    total: int
    page: int = 1
    page_size: int = 50


class AssetStatsResponse(BaseModel):
    """Asset statistics response."""
    total_assets: int
    by_type: Dict[str, int]
    by_status: Dict[str, int]
    by_namespace: Dict[str, int]


# ===== UPDATE MODELS =====

class UpdateEvaluationRequest(BaseModel):
    """Update evaluation request."""
    asset_id: Optional[str] = None
    current_version: str
    new_version: str
    asset_type: Optional[AssetType] = None


class UpdateEvaluationResponse(BaseModel):
    """Update evaluation response."""
    current_version: str
    new_version: str
    change_type: VersionChangeType
    decision: UpdateDecision
    safe: bool
    reason: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class UpdateRequest(BaseModel):
    """Update execution request."""
    asset_id: str
    target_version: str
    force: bool = False
    dry_run: bool = False


class UpdateResponse(BaseModel):
    """Update execution response."""
    asset_id: str
    status: str
    previous_version: str
    new_version: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    message: str
    rollback_available: bool = False


class UpdateHistoryResponse(BaseModel):
    """Update history entry."""
    id: str
    asset_id: str
    asset_name: str
    previous_version: str
    new_version: str
    change_type: VersionChangeType
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    rolled_back: bool = False


# ===== HEALTH CHECK MODELS =====

class HealthCheckResult(BaseModel):
    """Health check result."""
    check_type: str
    status: str
    message: str
    duration_ms: float
    timestamp: datetime


class HealthResponse(BaseModel):
    """System health response."""
    status: str
    version: str
    uptime_seconds: float
    checks: List[HealthCheckResult] = Field(default_factory=list)
    components: Dict[str, str] = Field(default_factory=dict)


# ===== CONFIGURATION MODELS =====

class ConfigResponse(BaseModel):
    """Configuration response."""
    auto_update_enabled: bool
    max_concurrent_updates: int
    semver_gates: Dict[str, str]
    rollback_enabled: bool
    monitoring_enabled: bool
    docker_enabled: bool
    kubernetes_enabled: bool


class ConfigUpdateRequest(BaseModel):
    """Configuration update request."""
    auto_update_enabled: Optional[bool] = None
    max_concurrent_updates: Optional[int] = Field(None, ge=1, le=100)
    dry_run_mode: Optional[bool] = None


# ===== SCAN MODELS =====

class ScanRequest(BaseModel):
    """Scan request."""
    docker: bool = True
    kubernetes: bool = True
    namespace: Optional[str] = "default"
    force_refresh: bool = False


class ScanResponse(BaseModel):
    """Scan execution response."""
    status: str
    assets_discovered: int
    docker_assets: int = 0
    kubernetes_assets: int = 0
    duration_seconds: float
    timestamp: datetime


# ===== METRICS MODELS =====

class MetricValue(BaseModel):
    """Single metric value."""
    name: str
    value: float
    labels: Dict[str, str] = Field(default_factory=dict)
    timestamp: datetime


class MetricsResponse(BaseModel):
    """Metrics summary response."""
    metrics: List[MetricValue]
    generated_at: datetime


# ===== ERROR MODELS =====

class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None
    code: str
    timestamp: datetime


# ===== ROLLBACK MODELS =====

class RollbackRequest(BaseModel):
    """Rollback request."""
    asset_id: str
    target_version: Optional[str] = None  # If None, rollback to previous


class RollbackResponse(BaseModel):
    """Rollback execution response."""
    asset_id: str
    status: str
    rolled_back_from: str
    rolled_back_to: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    message: str
