"""Unit tests for Config Loader."""

import pytest
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from utils.config_loader import ConfigLoader


class TestConfigLoader:
    """Tests for ConfigLoader class."""
    
    def test_load_config_valid(self):
        """Test loading valid configuration."""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('test_key: test_value\n')
            f.write('nested:\n')
            f.write('  key: value\n')
            config_path = f.name
        
        try:
            loader = ConfigLoader()
            config = loader.load_config(config_path)
            
            assert config['test_key'] == 'test_value'
            assert config['nested']['key'] == 'value'
        finally:
            Path(config_path).unlink()
    
    def test_load_config_nonexistent(self):
        """Test loading nonexistent configuration file."""
        loader = ConfigLoader()
        config = loader.load_config('/nonexistent/config.yaml')
        
        assert config == {}
    
    def test_get_simple_key(self):
        """Test getting a simple configuration value."""
        loader = ConfigLoader()
        loader.config = {'key': 'value'}
        
        result = loader.get('key')
        assert result == 'value'
    
    def test_get_nested_key(self):
        """Test getting a nested configuration value."""
        loader = ConfigLoader()
        loader.config = {'parent': {'child': 'value'}}
        
        result = loader.get('parent.child')
        assert result == 'value'
    
    def test_get_default_value(self):
        """Test getting default value for missing key."""
        loader = ConfigLoader()
        loader.config = {}
        
        result = loader.get('missing_key', 'default')
        assert result == 'default'
    
    def test_set_simple_key(self):
        """Test setting a simple configuration value."""
        loader = ConfigLoader()
        loader.config = {}
        
        loader.set('key', 'value')
        assert loader.config['key'] == 'value'
    
    def test_set_nested_key(self):
        """Test setting a nested configuration value."""
        loader = ConfigLoader()
        loader.config = {}
        
        loader.set('parent.child', 'value')
        assert loader.config['parent']['child'] == 'value'
