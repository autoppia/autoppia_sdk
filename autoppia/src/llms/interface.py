"""
Simple LLM Configuration Interface for Autoppia SDK

This module provides a simple, clean interface for LLM configuration
without framework-specific implementations or complex abstractions.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class LLMConfig:
    """Simple configuration for an LLM provider.
    
    This class holds the essential configuration needed to connect to any LLM provider
    without being tied to a specific framework implementation.
    """
    
    # Provider identification
    provider_name: str
    provider_type: str  # e.g., "openai", "anthropic", "google", "cohere", "huggingface"
    
    # Authentication
    api_key: str
    api_base: Optional[str] = None  # Custom API base URL
    
    # Model configuration
    model_name: str
    model_version: Optional[str] = None
    
    # Provider-specific configuration
    provider_config: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.provider_name:
            raise ValueError("provider_name is required")
        if not self.provider_type:
            raise ValueError("provider_type is required")
        if not self.api_key:
            raise ValueError("api_key is required")
        if not self.model_name:
            raise ValueError("model_name is required")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "provider_name": self.provider_name,
            "provider_type": self.provider_type,
            "api_key": self.api_key,
            "api_base": self.api_base,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "provider_config": self.provider_config or {},
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LLMConfig':
        """Create configuration from dictionary."""
        return cls(**data)
    
    def get_info(self) -> Dict[str, Any]:
        """Get basic provider information."""
        return {
            "provider_name": self.provider_name,
            "provider_type": self.provider_type,
            "model_name": self.model_name,
            "has_api_key": bool(self.api_key),
            "custom_base_url": bool(self.api_base),
            "additional_config": bool(self.provider_config)
        }


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    This interface focuses on:
    1. Provider configuration management
    2. Basic credential validation
    3. Provider information retrieval
    """
    
    def __init__(self, config: LLMConfig):
        """Initialize the LLM provider with configuration.
        
        Args:
            config: Provider configuration object
        """
        self.config = config
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """Validate the provider configuration.
        
        This method should implement provider-specific validation logic.
        """
        pass
    
    def validate_credentials(self) -> bool:
        """Validate that the API credentials are valid.
        
        Returns:
            True if credentials are valid, False otherwise
        """
        try:
            # Basic validation - check if API key exists and has reasonable length
            return bool(self.config.api_key and len(self.config.api_key) > 10)
        except Exception:
            return False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the provider.
        
        Returns:
            Dictionary containing provider information
        """
        return self.config.get_info()
    
    def get_config(self) -> LLMConfig:
        """Get the current provider configuration.
        
        Returns:
            Current configuration object
        """
        return self.config
    
    def update_config(self, **kwargs) -> None:
        """Update provider configuration.
        
        Args:
            **kwargs: Configuration updates
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        # Re-validate after update
        self._validate_config()
    
    def is_healthy(self) -> bool:
        """Check if the provider is healthy and accessible.
        
        Returns:
            True if provider is healthy, False otherwise
        """
        try:
            return self.validate_credentials()
        except Exception:
            return False
