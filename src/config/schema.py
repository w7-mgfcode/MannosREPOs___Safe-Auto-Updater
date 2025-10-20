"""
Configuration schema definitions using Pydantic.
"""

from enum import Enum
from typing import Optional, Dict, List
from pydantic import BaseModel, Field, field_validator


class UpdateAction(str, Enum):
    """Actions for different update types."""
    AUTO = "auto"
    REVIEW = "review"
    MANUAL = "manual"
    SKIP = "skip"


class HealthCheckType(str, Enum):
    """Types of health checks."""
    HTTP = "http"
    TCP = "tcp"
    EXEC = "exec"
    KUBERNETES = "kubernetes"


class SemVerGates(BaseModel):
    """Semantic versioning gate policies."""
    patch: UpdateAction = UpdateAction.AUTO
    minor: UpdateAction = UpdateAction.REVIEW
    major: UpdateAction = UpdateAction.MANUAL
    prerelease: UpdateAction = UpdateAction.MANUAL


class HTTPHealthCheck(BaseModel):
    """HTTP health check configuration."""
    endpoint: str = "/health"
    timeout: int = Field(default=30, ge=1, le=300)
    retries: int = Field(default=3, ge=1, le=10)
    expected_status: int = Field(default=200, ge=200, le=299)
    method: str = Field(default="GET")
    headers: Optional[Dict[str, str]] = None


class TCPHealthCheck(BaseModel):
    """TCP health check configuration."""
    port: int = Field(ge=1, le=65535)
    timeout: int = Field(default=10, ge=1, le=60)
    retries: int = Field(default=3, ge=1, le=10)


class ExecHealthCheck(BaseModel):
    """Exec health check configuration."""
    command: List[str]
    timeout: int = Field(default=30, ge=1, le=300)
    expected_exit_code: int = Field(default=0)


class HealthCheckConfig(BaseModel):
    """Health check configurations."""
    type: HealthCheckType
    http: Optional[HTTPHealthCheck] = None
    tcp: Optional[TCPHealthCheck] = None
    exec: Optional[ExecHealthCheck] = None

    @field_validator('http', 'tcp', 'exec')
    @classmethod
    def validate_health_check(cls, v, info):
        """Ensure health check config matches type."""
        if info.data.get('type') == HealthCheckType.HTTP and info.field_name == 'http' and v is None:
            raise ValueError("HTTP health check config required when type is HTTP")
        if info.data.get('type') == HealthCheckType.TCP and info.field_name == 'tcp' and v is None:
            raise ValueError("TCP health check config required when type is TCP")
        if info.data.get('type') == HealthCheckType.EXEC and info.field_name == 'exec' and v is None:
            raise ValueError("Exec health check config required when type is EXEC")
        return v


class RollbackConfig(BaseModel):
    """Rollback configuration."""
    auto_rollback: bool = True
    failure_threshold: float = Field(default=0.1, ge=0.0, le=1.0)
    monitoring_duration: int = Field(default=300, ge=60, le=3600)  # seconds
    max_rollback_attempts: int = Field(default=3, ge=1, le=10)


class UpdatePolicy(BaseModel):
    """Update policy configuration."""
    enabled: bool = True
    max_concurrent: int = Field(default=3, ge=1, le=100)
    update_window: Optional[str] = None  # Format: "HH:MM-HH:MM"
    dry_run: bool = False


class AutoUpdateConfig(BaseModel):
    """Auto-update configuration."""
    update_policy: UpdatePolicy = UpdatePolicy()
    semver_gates: SemVerGates = SemVerGates()
    health_checks: List[HealthCheckConfig] = []
    rollback: RollbackConfig = RollbackConfig()


class DockerConfig(BaseModel):
    """Docker configuration."""
    socket_path: str = "/var/run/docker.sock"
    watchtower_enabled: bool = False
    watchtower_endpoint: Optional[str] = None
    registry_credentials: Optional[Dict[str, Dict[str, str]]] = None


class KubernetesConfig(BaseModel):
    """Kubernetes configuration."""
    kubeconfig_path: Optional[str] = None
    namespace: str = "default"
    in_cluster: bool = False
    service_account: Optional[str] = None


class MonitoringConfig(BaseModel):
    """Monitoring and metrics configuration."""
    prometheus_enabled: bool = True
    prometheus_port: int = Field(default=9090, ge=1024, le=65535)
    metrics_path: str = "/metrics"
    log_level: str = Field(default="INFO")


class SafeUpdaterConfig(BaseModel):
    """Main configuration for Safe Auto-Updater."""
    auto_update: AutoUpdateConfig = AutoUpdateConfig()
    docker: DockerConfig = DockerConfig()
    kubernetes: KubernetesConfig = KubernetesConfig()
    monitoring: MonitoringConfig = MonitoringConfig()

    class Config:
        """Pydantic configuration."""
        use_enum_values = True
