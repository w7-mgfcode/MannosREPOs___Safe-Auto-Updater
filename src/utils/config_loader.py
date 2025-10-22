"""Configuration Loader

Loads and validates configuration from YAML files.
"""

import logging
import yaml
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Loads and manages configuration."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize config loader.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = {}
        
        if config_path:
            self.load_config(config_path)
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        logger.info(f"Loading configuration from: {config_path}")
        
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                logger.warning(f"Configuration file not found: {config_path}")
                return {}
            
            with open(config_file, 'r') as f:
                self.config = yaml.safe_load(f) or {}
            
            logger.info("Configuration loaded successfully")
            return self.config
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
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
    
    def set(self, key: str, value: Any):
        """Set a configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_config(self, config_path: Optional[str] = None):
        """Save configuration to YAML file.
        
        Args:
            config_path: Path to save configuration (uses loaded path if not specified)
        """
        save_path = config_path or self.config_path
        
        if not save_path:
            logger.error("No configuration path specified")
            return
        
        try:
            with open(save_path, 'w') as f:
                yaml.safe_dump(self.config, f, default_flow_style=False)
            
            logger.info(f"Configuration saved to: {save_path}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
