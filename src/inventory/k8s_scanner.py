"""
Kubernetes resource discovery and inventory.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from .state_manager import Asset, AssetType, AssetStatus, StateManager


class KubernetesScanner:
    """Scans and inventories Kubernetes resources."""

    def __init__(
        self,
        kubeconfig_path: Optional[str] = None,
        in_cluster: bool = False,
        namespace: str = "default",
        state_manager: Optional[StateManager] = None
    ):
        """
        Initialize Kubernetes scanner.

        Args:
            kubeconfig_path: Path to kubeconfig file.
            in_cluster: Use in-cluster configuration.
            namespace: Default namespace to scan.
            state_manager: Optional StateManager instance.

        Raises:
            Exception: If Kubernetes configuration fails.
        """
        try:
            if in_cluster:
                config.load_incluster_config()
            else:
                config.load_kube_config(config_file=kubeconfig_path)

            self.apps_v1 = client.AppsV1Api()
            self.core_v1 = client.CoreV1Api()
            self.namespace = namespace
            self.state_manager = state_manager or StateManager()

        except Exception as e:
            raise Exception(f"Failed to initialize Kubernetes client: {e}")

    def scan_all_resources(self, namespaces: Optional[List[str]] = None) -> List[Asset]:
        """
        Scan all supported Kubernetes resources.

        Args:
            namespaces: List of namespaces to scan. If None, scans default namespace.

        Returns:
            List of discovered assets.
        """
        assets = []
        target_namespaces = namespaces or [self.namespace]

        for ns in target_namespaces:
            assets.extend(self.scan_deployments(ns))
            assets.extend(self.scan_statefulsets(ns))
            assets.extend(self.scan_daemonsets(ns))

        return assets

    def scan_deployments(self, namespace: Optional[str] = None) -> List[Asset]:
        """
        Scan Kubernetes Deployments.

        Args:
            namespace: Namespace to scan.

        Returns:
            List of Deployment assets.
        """
        ns = namespace or self.namespace
        assets = []

        try:
            deployments = self.apps_v1.list_namespaced_deployment(ns)

            for deployment in deployments.items:
                asset = self._deployment_to_asset(deployment, ns)
                if asset:
                    assets.append(asset)
                    self.state_manager.add_asset(asset)

        except ApiException as e:
            print(f"Error scanning deployments in {ns}: {e}")

        return assets

    def scan_statefulsets(self, namespace: Optional[str] = None) -> List[Asset]:
        """
        Scan Kubernetes StatefulSets.

        Args:
            namespace: Namespace to scan.

        Returns:
            List of StatefulSet assets.
        """
        ns = namespace or self.namespace
        assets = []

        try:
            statefulsets = self.apps_v1.list_namespaced_stateful_set(ns)

            for statefulset in statefulsets.items:
                asset = self._statefulset_to_asset(statefulset, ns)
                if asset:
                    assets.append(asset)
                    self.state_manager.add_asset(asset)

        except ApiException as e:
            print(f"Error scanning statefulsets in {ns}: {e}")

        return assets

    def scan_daemonsets(self, namespace: Optional[str] = None) -> List[Asset]:
        """
        Scan Kubernetes DaemonSets.

        Args:
            namespace: Namespace to scan.

        Returns:
            List of DaemonSet assets.
        """
        ns = namespace or self.namespace
        assets = []

        try:
            daemonsets = self.apps_v1.list_namespaced_daemon_set(ns)

            for daemonset in daemonsets.items:
                asset = self._daemonset_to_asset(daemonset, ns)
                if asset:
                    assets.append(asset)
                    self.state_manager.add_asset(asset)

        except ApiException as e:
            print(f"Error scanning daemonsets in {ns}: {e}")

        return assets

    def _deployment_to_asset(self, deployment, namespace: str) -> Optional[Asset]:
        """Convert Deployment to Asset."""
        try:
            containers = deployment.spec.template.spec.containers
            # Use first container as primary
            main_container = containers[0]
            image = main_container.image
            version = self._extract_version(image)

            # Determine status
            status = self._determine_status(
                deployment.status.ready_replicas,
                deployment.spec.replicas
            )

            metadata = {
                'replicas': deployment.spec.replicas,
                'ready_replicas': deployment.status.ready_replicas or 0,
                'updated_replicas': deployment.status.updated_replicas or 0,
                'available_replicas': deployment.status.available_replicas or 0,
                'labels': deployment.metadata.labels or {},
                'annotations': deployment.metadata.annotations or {},
                'containers': [c.name for c in containers],
                'strategy': deployment.spec.strategy.type if deployment.spec.strategy else 'Unknown'
            }

            return Asset(
                id=f"k8s-deployment-{namespace}-{deployment.metadata.name}",
                name=deployment.metadata.name,
                asset_type=AssetType.K8S_DEPLOYMENT,
                namespace=namespace,
                current_version=version,
                image=image,
                status=status,
                last_updated=datetime.utcnow().isoformat(),
                metadata=metadata
            )

        except Exception as e:
            print(f"Error converting deployment {deployment.metadata.name}: {e}")
            return None

    def _statefulset_to_asset(self, statefulset, namespace: str) -> Optional[Asset]:
        """Convert StatefulSet to Asset."""
        try:
            containers = statefulset.spec.template.spec.containers
            main_container = containers[0]
            image = main_container.image
            version = self._extract_version(image)

            status = self._determine_status(
                statefulset.status.ready_replicas,
                statefulset.spec.replicas
            )

            metadata = {
                'replicas': statefulset.spec.replicas,
                'ready_replicas': statefulset.status.ready_replicas or 0,
                'current_replicas': statefulset.status.current_replicas or 0,
                'updated_replicas': statefulset.status.updated_replicas or 0,
                'labels': statefulset.metadata.labels or {},
                'annotations': statefulset.metadata.annotations or {},
                'containers': [c.name for c in containers],
                'service_name': statefulset.spec.service_name
            }

            return Asset(
                id=f"k8s-statefulset-{namespace}-{statefulset.metadata.name}",
                name=statefulset.metadata.name,
                asset_type=AssetType.K8S_STATEFULSET,
                namespace=namespace,
                current_version=version,
                image=image,
                status=status,
                last_updated=datetime.utcnow().isoformat(),
                metadata=metadata
            )

        except Exception as e:
            print(f"Error converting statefulset {statefulset.metadata.name}: {e}")
            return None

    def _daemonset_to_asset(self, daemonset, namespace: str) -> Optional[Asset]:
        """Convert DaemonSet to Asset."""
        try:
            containers = daemonset.spec.template.spec.containers
            main_container = containers[0]
            image = main_container.image
            version = self._extract_version(image)

            status = self._determine_status(
                daemonset.status.number_ready,
                daemonset.status.desired_number_scheduled
            )

            metadata = {
                'desired_number_scheduled': daemonset.status.desired_number_scheduled or 0,
                'current_number_scheduled': daemonset.status.current_number_scheduled or 0,
                'number_ready': daemonset.status.number_ready or 0,
                'updated_number_scheduled': daemonset.status.updated_number_scheduled or 0,
                'labels': daemonset.metadata.labels or {},
                'annotations': daemonset.metadata.annotations or {},
                'containers': [c.name for c in containers]
            }

            return Asset(
                id=f"k8s-daemonset-{namespace}-{daemonset.metadata.name}",
                name=daemonset.metadata.name,
                asset_type=AssetType.K8S_DAEMONSET,
                namespace=namespace,
                current_version=version,
                image=image,
                status=status,
                last_updated=datetime.utcnow().isoformat(),
                metadata=metadata
            )

        except Exception as e:
            print(f"Error converting daemonset {daemonset.metadata.name}: {e}")
            return None

    def _extract_version(self, image: str) -> str:
        """Extract version from image string."""
        if ':' in image:
            return image.split(':')[-1]
        return 'latest'

    def _determine_status(self, ready: Optional[int], desired: Optional[int]) -> AssetStatus:
        """
        Determine asset status based on replica counts.

        Args:
            ready: Number of ready replicas.
            desired: Desired number of replicas.

        Returns:
            AssetStatus enum value.
        """
        if ready is None or desired is None:
            return AssetStatus.UNKNOWN

        if ready == desired and desired > 0:
            return AssetStatus.ACTIVE
        elif ready > 0:
            return AssetStatus.UPDATING
        else:
            return AssetStatus.FAILED

    def get_pod_health(self, namespace: str, label_selector: str) -> Dict[str, Any]:
        """
        Get health status of pods matching label selector.

        Args:
            namespace: Namespace to query.
            label_selector: Kubernetes label selector.

        Returns:
            Dictionary with pod health information.
        """
        try:
            pods = self.core_v1.list_namespaced_pod(
                namespace=namespace,
                label_selector=label_selector
            )

            total = len(pods.items)
            ready = sum(1 for pod in pods.items if pod.status.phase == 'Running')
            failed = sum(1 for pod in pods.items if pod.status.phase == 'Failed')

            return {
                'total': total,
                'ready': ready,
                'failed': failed,
                'pending': total - ready - failed,
                'health_percentage': (ready / total * 100) if total > 0 else 0
            }

        except ApiException as e:
            print(f"Error getting pod health: {e}")
            return {'total': 0, 'ready': 0, 'failed': 0, 'pending': 0, 'health_percentage': 0}
