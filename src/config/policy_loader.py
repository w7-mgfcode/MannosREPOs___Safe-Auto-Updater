"""
Configuration and policy loader for Safe Auto-Updater.
"""

import os
from pathlib import Path
from typing import Optional
import yaml
from .schema import SafeUpdaterConfig


class PolicyLoader:
    """Loads and validates configuration policies."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize policy loader.

        Args:
            config_path: Path to configuration file. If None, uses default locations.
        """
        self.config_path = config_path or self._find_config()

    def _find_config(self) -> Optional[str]:
        """
        Find configuration file in standard locations.

        Returns:
            Path to configuration file or None if not found.
        """
        search_paths = [
            os.getenv("SAFE_UPDATER_CONFIG"),
            "./config/policy.yaml",
            "./policy.yaml",
            "/etc/safe-updater/policy.yaml",
            str(Path.home() / ".safe-updater" / "policy.yaml"),
        ]

        for path in search_paths:
            if path and Path(path).exists():
                return path

        return None

    def load(self) -> SafeUpdaterConfig:
        """
        Load and validate configuration.

        Returns:
            Validated SafeUpdaterConfig instance.

        Raises:
            FileNotFoundError: If config file not found.
            yaml.YAMLError: If YAML parsing fails.
            pydantic.ValidationError: If validation fails.
        """
        if not self.config_path:
            # Return default configuration
            return SafeUpdaterConfig()

        with open(self.config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)

        if config_data is None:
            return SafeUpdaterConfig()

        return SafeUpdaterConfig(**config_data)

    def validate(self, config_data: dict) -> SafeUpdaterConfig:
        """
        Validate configuration data without loading from file.

        Args:
            config_data: Configuration dictionary.

        Returns:
            Validated SafeUpdaterConfig instance.
        """
        return SafeUpdaterConfig(**config_data)

    def save(self, config: SafeUpdaterConfig, output_path: str):
        """
        Save configuration to YAML file.

        Args:
            config: SafeUpdaterConfig instance to save.
            output_path: Path to output file.
        """
        config_dict = config.model_dump(exclude_none=True)

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)


def load_config(config_path: Optional[str] = None) -> SafeUpdaterConfig:
    """
    Convenience function to load configuration.

    Args:
        config_path: Optional path to configuration file.

    Returns:
        SafeUpdaterConfig instance.
    """
    loader = PolicyLoader(config_path)
    return loader.load()
