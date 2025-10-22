"""
Docker container discovery and inventory.
"""

from typing import List, Optional, Dict, Any
import docker
from docker.errors import DockerException
from datetime import datetime
from .state_manager import Asset, AssetType, AssetStatus, StateManager


class DockerScanner:
    """Scans and inventories Docker containers."""

    def __init__(
        self,
        socket_path: str = "/var/run/docker.sock",
        state_manager: Optional[StateManager] = None
    ):
        """
        Initialize Docker scanner.

        Args:
            socket_path: Path to Docker socket.
            state_manager: Optional StateManager instance.

        Raises:
            DockerException: If Docker connection fails.
        """
        try:
            self.client = docker.DockerClient(base_url=f"unix://{socket_path}")
            self.client.ping()  # Verify connection
        except DockerException as e:
            raise DockerException(f"Failed to connect to Docker: {e}")

        self.state_manager = state_manager or StateManager()

    def scan_containers(self, include_stopped: bool = False) -> List[Asset]:
        """
        Scan all Docker containers.

        Args:
            include_stopped: Include stopped containers.

        Returns:
            List of discovered container assets.
        """
        assets = []

        try:
            containers = self.client.containers.list(all=include_stopped)

            for container in containers:
                asset = self._container_to_asset(container)
                if asset:
                    assets.append(asset)
                    self.state_manager.add_asset(asset)

        except DockerException as e:
            print(f"Error scanning containers: {e}")

        return assets

    def _container_to_asset(self, container) -> Optional[Asset]:
        """
        Convert Docker container to Asset.

        Args:
            container: Docker container object.

        Returns:
            Asset instance or None if conversion fails.
        """
        try:
            container.reload()  # Refresh container data

            # Extract image and version
            image_name = container.image.tags[0] if container.image.tags else "unknown"
            version = self._extract_version(image_name)

            # Determine status
            status = AssetStatus.ACTIVE if container.status == 'running' else AssetStatus.UNKNOWN

            # Build metadata
            metadata = {
                'docker_id': container.id,
                'short_id': container.short_id,
                'status': container.status,
                'created': container.attrs.get('Created', ''),
                'labels': container.labels,
                'networks': list(container.attrs.get('NetworkSettings', {}).get('Networks', {}).keys()),
                'ports': self._extract_ports(container),
                'environment': self._extract_env_vars(container),
            }

            asset = Asset(
                id=f"docker-{container.id}",
                name=container.name,
                asset_type=AssetType.DOCKER_CONTAINER,
                namespace=None,  # Docker doesn't have namespaces
                current_version=version,
                image=image_name,
                status=status,
                last_updated=datetime.utcnow().isoformat(),
                metadata=metadata
            )

            return asset

        except Exception as e:
            print(f"Error converting container {container.name}: {e}")
            return None

    def _extract_version(self, image_name: str) -> str:
        """
        Extract version from image name.

        Args:
            image_name: Docker image name (e.g., nginx:1.21.0)

        Returns:
            Version string or 'latest'.
        """
        if ':' in image_name:
            return image_name.split(':')[-1]
        return 'latest'

    def _extract_ports(self, container) -> Dict[str, Any]:
        """
        Extract port mappings from container.

        Args:
            container: Docker container object.

        Returns:
            Dictionary of port mappings.
        """
        try:
            ports = container.attrs.get('NetworkSettings', {}).get('Ports', {})
            return {k: v for k, v in ports.items() if v}
        except Exception:
            return {}

    def _extract_env_vars(self, container) -> List[str]:
        """
        Extract environment variables (non-sensitive).

        Args:
            container: Docker container object.

        Returns:
            List of environment variable names (values hidden for security).
        """
        try:
            env = container.attrs.get('Config', {}).get('Env', [])
            # Only return variable names, not values (security)
            return [e.split('=')[0] for e in env]
        except Exception:
            return []

    def get_container_health(self, container_id: str) -> Optional[str]:
        """
        Get container health status.

        Args:
            container_id: Container ID or name.

        Returns:
            Health status string or None.
        """
        try:
            container = self.client.containers.get(container_id)
            health = container.attrs.get('State', {}).get('Health', {})
            return health.get('Status')
        except DockerException:
            return None

    def get_container_logs(
        self,
        container_id: str,
        tail: int = 100
    ) -> Optional[str]:
        """
        Get recent container logs.

        Args:
            container_id: Container ID or name.
            tail: Number of lines to retrieve.

        Returns:
            Log output or None.
        """
        try:
            container = self.client.containers.get(container_id)
            logs = container.logs(tail=tail, timestamps=True)
            return logs.decode('utf-8')
        except DockerException:
            return None

    def get_image_digest(self, image_name: str) -> Optional[str]:
        """
        Get image digest (SHA256).

        Args:
            image_name: Image name with tag.

        Returns:
            Image digest or None.
        """
        try:
            image = self.client.images.get(image_name)
            # Get the RepoDigests
            digests = image.attrs.get('RepoDigests', [])
            return digests[0] if digests else None
        except DockerException:
            return None

    def close(self):
        """Close Docker client connection."""
        self.client.close()
