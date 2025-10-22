"""
Health check engine for validating service health post-update.
"""

import time
import socket
import requests
from typing import Optional, List
from dataclasses import dataclass
from enum import Enum
from kubernetes import client
from ..config.schema import HealthCheckConfig, HTTPHealthCheck, TCPHealthCheck
from ..inventory.state_manager import Asset


class HealthStatus(str, Enum):
    """Health check status."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of health check operation."""
    status: HealthStatus
    healthy: bool
    ready_replicas: int
    total_replicas: int
    health_percentage: float
    checks_passed: List[str]
    checks_failed: List[str]
    message: str
    details: Optional[dict] = None


class HealthChecker:
    """Multi-type health check engine."""

    def __init__(self, k8s_apps_api: Optional[client.AppsV1Api] = None,
                 k8s_core_api: Optional[client.CoreV1Api] = None):
        """
        Initialize health checker.

        Args:
            k8s_apps_api: Kubernetes Apps API client.
            k8s_core_api: Kubernetes Core API client.
        """
        self.k8s_apps_api = k8s_apps_api
        self.k8s_core_api = k8s_core_api

    def check(
        self,
        config: HealthCheckConfig,
        asset: Optional[Asset] = None
    ) -> HealthCheckResult:
        """
        Execute health check based on configuration.

        Args:
            config: Health check configuration.
            asset: Asset to check (for Kubernetes checks).

        Returns:
            HealthCheckResult with check details.
        """
        if config.type == "http" and config.http:
            return self.check_http(config.http)
        elif config.type == "tcp" and config.tcp:
            return self.check_tcp(config.tcp)
        elif config.type == "kubernetes" and asset:
            return self.check_kubernetes(asset)
        else:
            return HealthCheckResult(
                status=HealthStatus.UNKNOWN,
                healthy=False,
                ready_replicas=0,
                total_replicas=0,
                health_percentage=0.0,
                checks_passed=[],
                checks_failed=["Invalid configuration"],
                message="Invalid health check configuration"
            )

    def check_http(
        self,
        config: HTTPHealthCheck,
        base_url: Optional[str] = None
    ) -> HealthCheckResult:
        """
        Execute HTTP health check.

        Args:
            config: HTTP health check configuration.
            base_url: Base URL (if not in endpoint).

        Returns:
            HealthCheckResult.
        """
        url = config.endpoint
        if base_url and not config.endpoint.startswith('http'):
            url = f"{base_url.rstrip('/')}/{config.endpoint.lstrip('/')}"

        checks_passed = []
        checks_failed = []

        for attempt in range(config.retries):
            try:
                response = requests.request(
                    method=config.method,
                    url=url,
                    headers=config.headers or {},
                    timeout=config.timeout,
                    verify=True  # SSL verification
                )

                # Check status code
                if config.expected_status <= response.status_code < config.expected_status + 100:
                    checks_passed.append(f"HTTP {response.status_code} (attempt {attempt + 1})")

                    return HealthCheckResult(
                        status=HealthStatus.HEALTHY,
                        healthy=True,
                        ready_replicas=1,
                        total_replicas=1,
                        health_percentage=100.0,
                        checks_passed=checks_passed,
                        checks_failed=checks_failed,
                        message=f"HTTP health check passed: {response.status_code}",
                        details={'status_code': response.status_code, 'url': url}
                    )
                else:
                    checks_failed.append(
                        f"Unexpected status {response.status_code} (attempt {attempt + 1})"
                    )

            except requests.exceptions.Timeout:
                checks_failed.append(f"Timeout after {config.timeout}s (attempt {attempt + 1})")
            except requests.exceptions.ConnectionError:
                checks_failed.append(f"Connection failed (attempt {attempt + 1})")
            except Exception as e:
                checks_failed.append(f"Error: {str(e)} (attempt {attempt + 1})")

            # Wait before retry (except on last attempt)
            if attempt < config.retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff

        return HealthCheckResult(
            status=HealthStatus.UNHEALTHY,
            healthy=False,
            ready_replicas=0,
            total_replicas=1,
            health_percentage=0.0,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            message=f"HTTP health check failed after {config.retries} attempts",
            details={'url': url}
        )

    def check_tcp(self, config: TCPHealthCheck, host: str = "localhost") -> HealthCheckResult:
        """
        Execute TCP health check.

        Args:
            config: TCP health check configuration.
            host: Hostname or IP address.

        Returns:
            HealthCheckResult.
        """
        checks_passed = []
        checks_failed = []

        for attempt in range(config.retries):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(config.timeout)

                result = sock.connect_ex((host, config.port))

                sock.close()

                if result == 0:
                    checks_passed.append(f"TCP port {config.port} open (attempt {attempt + 1})")

                    return HealthCheckResult(
                        status=HealthStatus.HEALTHY,
                        healthy=True,
                        ready_replicas=1,
                        total_replicas=1,
                        health_percentage=100.0,
                        checks_passed=checks_passed,
                        checks_failed=checks_failed,
                        message=f"TCP port {config.port} is accessible",
                        details={'host': host, 'port': config.port}
                    )
                else:
                    checks_failed.append(
                        f"TCP port {config.port} closed (attempt {attempt + 1})"
                    )

            except socket.timeout:
                checks_failed.append(f"Timeout (attempt {attempt + 1})")
            except Exception as e:
                checks_failed.append(f"Error: {str(e)} (attempt {attempt + 1})")

            # Wait before retry
            if attempt < config.retries - 1:
                time.sleep(2 ** attempt)

        return HealthCheckResult(
            status=HealthStatus.UNHEALTHY,
            healthy=False,
            ready_replicas=0,
            total_replicas=1,
            health_percentage=0.0,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            message=f"TCP health check failed after {config.retries} attempts",
            details={'host': host, 'port': config.port}
        )

    def check_kubernetes(self, asset: Asset) -> HealthCheckResult:
        """
        Execute Kubernetes-native health check using readiness probes.

        Args:
            asset: Asset to check (Deployment, StatefulSet, DaemonSet).

        Returns:
            HealthCheckResult.
        """
        if not self.k8s_apps_api or not self.k8s_core_api:
            return HealthCheckResult(
                status=HealthStatus.UNKNOWN,
                healthy=False,
                ready_replicas=0,
                total_replicas=0,
                health_percentage=0.0,
                checks_passed=[],
                checks_failed=["Kubernetes API not configured"],
                message="Kubernetes API client not available"
            )

        namespace = asset.namespace or "default"
        resource_name = asset.name

        try:
            # Check based on asset type
            if asset.asset_type.value == "k8s_deployment":
                return self._check_deployment(resource_name, namespace)
            elif asset.asset_type.value == "k8s_statefulset":
                return self._check_statefulset(resource_name, namespace)
            elif asset.asset_type.value == "k8s_daemonset":
                return self._check_daemonset(resource_name, namespace)
            else:
                return HealthCheckResult(
                    status=HealthStatus.UNKNOWN,
                    healthy=False,
                    ready_replicas=0,
                    total_replicas=0,
                    health_percentage=0.0,
                    checks_passed=[],
                    checks_failed=[f"Unsupported asset type: {asset.asset_type}"],
                    message="Cannot perform Kubernetes health check on this asset type"
                )

        except Exception as e:
            return HealthCheckResult(
                status=HealthStatus.UNKNOWN,
                healthy=False,
                ready_replicas=0,
                total_replicas=0,
                health_percentage=0.0,
                checks_passed=[],
                checks_failed=[f"API error: {str(e)}"],
                message=f"Kubernetes API error: {str(e)}"
            )

    def _check_deployment(self, name: str, namespace: str) -> HealthCheckResult:
        """Check Deployment health."""
        deployment = self.k8s_apps_api.read_namespaced_deployment(name, namespace)

        desired = deployment.spec.replicas or 0
        ready = deployment.status.ready_replicas or 0
        updated = deployment.status.updated_replicas or 0
        available = deployment.status.available_replicas or 0

        health_percentage = (ready / desired * 100) if desired > 0 else 0.0

        checks_passed = []
        checks_failed = []

        if ready == desired:
            checks_passed.append(f"All {ready}/{desired} replicas ready")
        else:
            checks_failed.append(f"Only {ready}/{desired} replicas ready")

        if updated == desired:
            checks_passed.append(f"All {updated} replicas updated")
        else:
            checks_failed.append(f"Only {updated}/{desired} replicas updated")

        # Determine status
        if ready == desired and updated == desired:
            status = HealthStatus.HEALTHY
            healthy = True
        elif ready > 0:
            status = HealthStatus.DEGRADED
            healthy = False
        else:
            status = HealthStatus.UNHEALTHY
            healthy = False

        return HealthCheckResult(
            status=status,
            healthy=healthy,
            ready_replicas=ready,
            total_replicas=desired,
            health_percentage=health_percentage,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            message=f"Deployment: {ready}/{desired} replicas ready ({health_percentage:.1f}%)",
            details={
                'desired': desired,
                'ready': ready,
                'updated': updated,
                'available': available
            }
        )

    def _check_statefulset(self, name: str, namespace: str) -> HealthCheckResult:
        """Check StatefulSet health."""
        statefulset = self.k8s_apps_api.read_namespaced_stateful_set(name, namespace)

        desired = statefulset.spec.replicas or 0
        ready = statefulset.status.ready_replicas or 0
        current = statefulset.status.current_replicas or 0

        health_percentage = (ready / desired * 100) if desired > 0 else 0.0

        checks_passed = []
        checks_failed = []

        if ready == desired:
            checks_passed.append(f"All {ready}/{desired} replicas ready")
            status = HealthStatus.HEALTHY
            healthy = True
        elif ready > 0:
            checks_failed.append(f"Only {ready}/{desired} replicas ready")
            status = HealthStatus.DEGRADED
            healthy = False
        else:
            checks_failed.append(f"No replicas ready (0/{desired})")
            status = HealthStatus.UNHEALTHY
            healthy = False

        return HealthCheckResult(
            status=status,
            healthy=healthy,
            ready_replicas=ready,
            total_replicas=desired,
            health_percentage=health_percentage,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            message=f"StatefulSet: {ready}/{desired} replicas ready ({health_percentage:.1f}%)"
        )

    def _check_daemonset(self, name: str, namespace: str) -> HealthCheckResult:
        """Check DaemonSet health."""
        daemonset = self.k8s_apps_api.read_namespaced_daemon_set(name, namespace)

        desired = daemonset.status.desired_number_scheduled or 0
        ready = daemonset.status.number_ready or 0

        health_percentage = (ready / desired * 100) if desired > 0 else 0.0

        checks_passed = []
        checks_failed = []

        if ready == desired:
            checks_passed.append(f"All {ready}/{desired} pods ready")
            status = HealthStatus.HEALTHY
            healthy = True
        elif ready > 0:
            checks_failed.append(f"Only {ready}/{desired} pods ready")
            status = HealthStatus.DEGRADED
            healthy = False
        else:
            checks_failed.append(f"No pods ready (0/{desired})")
            status = HealthStatus.UNHEALTHY
            healthy = False

        return HealthCheckResult(
            status=status,
            healthy=healthy,
            ready_replicas=ready,
            total_replicas=desired,
            health_percentage=health_percentage,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            message=f"DaemonSet: {ready}/{desired} pods ready ({health_percentage:.1f}%)"
        )

    def wait_for_healthy(
        self,
        asset: Asset,
        timeout: int = 300,
        check_interval: int = 10
    ) -> HealthCheckResult:
        """
        Wait for asset to become healthy.

        Args:
            asset: Asset to monitor.
            timeout: Maximum wait time in seconds.
            check_interval: Seconds between checks.

        Returns:
            Final HealthCheckResult.
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            result = self.check_kubernetes(asset)

            if result.healthy:
                return result

            if result.status == HealthStatus.UNHEALTHY:
                # Still wait, might recover
                pass

            time.sleep(check_interval)

        # Timeout reached
        final_result = self.check_kubernetes(asset)
        final_result.message += f" (timeout after {timeout}s)"

        return final_result
