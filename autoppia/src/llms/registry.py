"""
Simple LLM Configuration Registry for Autoppia SDK

This module provides a simple registry for managing LLM configurations
without complex provider management or framework-specific implementations.
"""

import logging
from typing import Dict, Any, Optional, List
from .interface import LLMConfig

logger = logging.getLogger(__name__)


class LLMRegistry:
    """
    Simple registry for managing LLM configurations.
    
    This registry allows developers to:
    1. Store and retrieve LLM configurations
    2. List available configurations
    3. Set a default configuration
    4. Basic validation of configurations
    """
    
    def __init__(self):
        """Initialize the registry."""
        self._configs: Dict[str, LLMConfig] = {}
        self._default_config: Optional[str] = None
    
    def add_config(self, name: str, config: LLMConfig) -> None:
        """Add an LLM configuration to the registry.
        
        Args:
            name: Unique name for the configuration
            config: LLM configuration object
        """
        if not isinstance(config, LLMConfig):
            raise ValueError("Config must be an LLMConfig instance")
        
        self._configs[name] = config
        logger.info(f"Added LLM config: {name} ({config.provider_type})")
        
        # Set as default if it's the first one
        if self._default_config is None:
            self._default_config = name
    
    def get_config(self, name: Optional[str] = None) -> Optional[LLMConfig]:
        """Get a configuration by name.
        
        Args:
            name: Configuration name (uses default if None)
            
        Returns:
            Configuration object or None if not found
        """
        config_name = name or self._default_config
        if not config_name:
            logger.warning("No default config set")
            return None
        
        config = self._configs.get(config_name)
        if not config:
            logger.warning(f"Config '{config_name}' not found")
            return None
        
        return config
    
    def list_configs(self) -> List[Dict[str, Any]]:
        """List all configurations with their information.
        
        Returns:
            List of configuration information dictionaries
        """
        configs_info = []
        for name, config in self._configs.items():
            info = {
                "name": name,
                "type": config.provider_type,
                "model": config.model_name,
                "provider_name": config.provider_name,
                "is_default": (name == self._default_config)
            }
            configs_info.append(info)
        return configs_info
    
    def set_default_config(self, name: str) -> bool:
        """Set the default configuration.
        
        Args:
            name: Name of the configuration to set as default
            
        Returns:
            True if successful, False if configuration not found
        """
        if name not in self._configs:
            logger.error(f"Cannot set default config: '{name}' not found")
            return False
        
        self._default_config = name
        logger.info(f"Set default config to: {name}")
        return True
    
    def remove_config(self, name: str) -> bool:
        """Remove a configuration from the registry.
        
        Args:
            name: Name of the configuration to remove
            
        Returns:
            True if successful, False if configuration not found
        """
        if name not in self._configs:
            return False
        
        # Don't allow removing the default config if it's the only one
        if len(self._configs) == 1:
            logger.warning("Cannot remove the last configuration")
            return False
        
        removed_config = self._configs.pop(name)
        logger.info(f"Removed config: {name}")
        
        # Update default config if necessary
        if name == self._default_config:
            # Set first available config as default
            self._default_config = next(iter(self._configs.keys()))
            logger.info(f"Updated default config to: {self._default_config}")
        
        return True
    
    def clear_configs(self) -> None:
        """Clear all configurations."""
        self._configs.clear()
        self._default_config = None
        logger.info("Cleared all LLM configurations")
    
    def get_registry_info(self) -> Dict[str, Any]:
        """Get registry information.
        
        Returns:
            Dictionary containing registry status and information
        """
        return {
            "total_configs": len(self._configs),
            "default_config": self._default_config,
            "available_provider_types": list(set(c.provider_type for c in self._configs.values())),
            "configs": self.list_configs()
        }


# Global registry instance
def get_llm_registry() -> LLMRegistry:
    """Get the global LLM registry instance."""
    return LLMRegistry()


# Convenience functions
def add_llm_config(name: str, config: LLMConfig) -> None:
    """Add a configuration to the global registry."""
    get_llm_registry().add_config(name, config)


def get_llm_config(name: Optional[str] = None) -> Optional[LLMConfig]:
    """Get a configuration from the global registry."""
    return get_llm_registry().get_config(name)


def list_llm_configs() -> List[Dict[str, Any]]:
    """List all configurations from the global registry."""
    return get_llm_registry().list_configs() 