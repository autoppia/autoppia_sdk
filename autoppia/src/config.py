"""
Configuration Management for Autoppia SDK

This module provides centralized configuration management including environment variables,
configuration files, and runtime configuration options.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class SDKConfig:
    """Main configuration class for Autoppia SDK."""
    
    # API Configuration
    api_key: Optional[str] = None
    base_url: str = "https://api-automata.autoppia.com/api/v1"
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Worker Configuration
    default_worker_timeout: int = 300
    max_worker_instances: int = 10
    
    # LLM Configuration
    default_llm_provider: str = "openai"
    default_llm_model: str = "gpt-4o"
    
    # Integration Configuration
    enable_web_search: bool = True
    enable_email: bool = False
    enable_database: bool = False
    
    # Development Configuration
    debug_mode: bool = False
    enable_metrics: bool = True
    
    def __post_init__(self):
        """Post-initialization setup."""
        self._load_environment_variables()
        self._setup_logging()
    
    def _load_environment_variables(self):
        """Load configuration from environment variables."""
        env_mapping = {
            'AUTOPPIA_API_KEY': 'api_key',
            'AUTOPPIA_BASE_URL': 'base_url',
            'AUTOPPIA_LOG_LEVEL': 'log_level',
            'AUTOPPIA_DEBUG': 'debug_mode',
            'AUTOPPIA_DEFAULT_LLM_PROVIDER': 'default_llm_provider',
            'AUTOPPIA_DEFAULT_LLM_MODEL': 'default_llm_model',
        }
        
        for env_var, attr_name in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                if attr_name == 'debug_mode':
                    setattr(self, attr_name, value.lower() in ('true', '1', 'yes'))
                elif attr_name in ('default_worker_timeout', 'max_worker_instances'):
                    setattr(self, attr_name, int(value))
                else:
                    setattr(self, attr_name, value)
    
    def _setup_logging(self):
        """Configure logging based on configuration."""
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format=self.log_format
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'api_key': self.api_key,
            'base_url': self.base_url,
            'log_level': self.log_level,
            'default_worker_timeout': self.default_worker_timeout,
            'max_worker_instances': self.max_worker_instances,
            'default_llm_provider': self.default_llm_provider,
            'default_llm_model': self.default_llm_model,
            'enable_web_search': self.enable_web_search,
            'enable_email': self.enable_email,
            'enable_database': self.enable_database,
            'debug_mode': self.debug_mode,
            'enable_metrics': self.enable_metrics,
        }
    
    def save_to_file(self, file_path: str) -> None:
        """Save configuration to a JSON file."""
        config_data = self.to_dict()
        # Remove sensitive data
        if 'api_key' in config_data:
            config_data['api_key'] = '***' if config_data['api_key'] else None
        
        with open(file_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        logger.info(f"Configuration saved to {file_path}")
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'SDKConfig':
        """Load configuration from a JSON file."""
        if not os.path.exists(file_path):
            logger.warning(f"Configuration file {file_path} not found, using defaults")
            return cls()
        
        try:
            with open(file_path, 'r') as f:
                config_data = json.load(f)
            
            # Create config instance and update with file data
            config = cls()
            for key, value in config_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            
            logger.info(f"Configuration loaded from {file_path}")
            return config
        except Exception as e:
            logger.error(f"Error loading configuration from {file_path}: {e}")
            return cls()
    
    @classmethod
    def get_default_config_path(cls) -> str:
        """Get the default configuration file path."""
        home_dir = Path.home()
        config_dir = home_dir / ".autoppia"
        config_dir.mkdir(exist_ok=True)
        return str(config_dir / "config.json")


# Global configuration instance
_config: Optional[SDKConfig] = None


def get_config() -> SDKConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        # Try to load from default location, fall back to defaults
        default_path = SDKConfig.get_default_config_path()
        _config = SDKConfig.load_from_file(default_path)
    return _config


def set_config(config: SDKConfig) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config


def reset_config() -> None:
    """Reset the global configuration to defaults."""
    global _config
    _config = None
