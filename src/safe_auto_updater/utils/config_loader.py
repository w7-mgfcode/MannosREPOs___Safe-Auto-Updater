"""
Configuration Loader

Loads and validates configuration files.
"""

from typing import Dict, Any, Optional
import logging
import yaml
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Loads and manages configuration."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration loader.

        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        logger.info("ConfigLoader initialized")

    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration from file.

        Args:
            config_path: Path to configuration file (overrides instance path)

        Returns:
            Configuration dictionary
        """
        path = config_path or self.config_path

        if not path:
            logger.warning("No configuration path provided")
            return {}

        try:
            config_file = Path(path)
            
            if not config_file.exists():
                logger.error(f"Configuration file not found: {path}")
                return {}

            # Load based on file extension
            if config_file.suffix in ['.yaml', '.yml']:
                with open(config_file, 'r') as f:
                    self.config = yaml.safe_load(f) or {}
            elif config_file.suffix == '.json':
                with open(config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                logger.error(f"Unsupported configuration format: {config_file.suffix}")
                return {}

            logger.info(f"Configuration loaded from {path}")
            return self.config

        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return {}

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.

        Args:
            key: Configuration key (supports dot notation for nested keys)
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def validate_config(self) -> bool:
        """
        Validate configuration structure and required fields.

        Returns:
            True if valid, False otherwise
        """
        required_keys = [
            'inventory',
            'detection',
            'execution'
        ]

        for key in required_keys:
            if key not in self.config:
                logger.error(f"Missing required configuration key: {key}")
                return False

        logger.info("Configuration validation passed")
        return True
