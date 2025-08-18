"""
Framework-Agnostic LLM Provider Interface for Autoppia SDK

This module provides a flexible interface for LLM providers that is not tied to
any specific framework (LangChain, OpenAI Assistants, LlamaIndex, etc.).
It focuses on provider configuration and credentials management.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass


@dataclass
class LLMProviderConfig:
    """Configuration for an LLM provider.
    
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
    
    # Framework preferences (optional)
    preferred_framework: Optional[str] = None  # e.g., "langchain", "openai_assistants", "llamaindex"
    
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
            "preferred_framework": self.preferred_framework
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LLMProviderConfig':
        """Create configuration from dictionary."""
        return cls(**data)


class LLMProviderInterface(ABC):
    """
    Abstract base class for LLM providers.
    
    This interface is framework-agnostic and focuses on:
    1. Provider configuration management
    2. Credential validation
    3. Framework-specific adapter creation
    4. Health checking and status monitoring
    """
    
    def __init__(self, config: LLMProviderConfig):
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
    
    @abstractmethod
    def validate_credentials(self) -> bool:
        """Validate that the API credentials are valid.
        
        Returns:
            True if credentials are valid, False otherwise
        """
        pass
    
    @abstractmethod
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the provider.
        
        Returns:
            Dictionary containing provider information
        """
        pass
    
    def create_langchain_adapter(self) -> Any:
        """Create a LangChain adapter for this provider.
        
        Returns:
            LangChain-compatible LLM instance
            
        Raises:
            NotImplementedError: If LangChain adapter is not supported
        """
        raise NotImplementedError(f"LangChain adapter not supported for {self.config.provider_type}")
    
    def create_openai_assistants_adapter(self) -> Any:
        """Create an OpenAI Assistants adapter for this provider.
        
        Returns:
            OpenAI Assistants-compatible client
            
        Raises:
            NotImplementedError: If OpenAI Assistants adapter is not supported
        """
        raise NotImplementedError(f"OpenAI Assistants adapter not supported for {self.config.provider_type}")
    
    def create_llamaindex_adapter(self) -> Any:
        """Create a LlamaIndex adapter for this provider.
        
        Returns:
            LlamaIndex-compatible LLM instance
            
        Raises:
            NotImplementedError: If LlamaIndex adapter is not supported
        """
        raise NotImplementedError(f"LlamaIndex adapter not supported for {self.config.provider_type}")
    
    def create_custom_adapter(self, framework: str, **kwargs) -> Any:
        """Create a custom framework adapter.
        
        Args:
            framework: Name of the framework
            **kwargs: Additional framework-specific arguments
            
        Returns:
            Framework-specific adapter instance
            
        Raises:
            NotImplementedError: If custom framework adapter is not supported
        """
        raise NotImplementedError(f"Custom framework '{framework}' adapter not supported for {self.config.provider_type}")
    
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
    
    def get_config(self) -> LLMProviderConfig:
        """Get the current provider configuration.
        
        Returns:
            Current configuration object
        """
        return self.config
    
    def is_healthy(self) -> bool:
        """Check if the provider is healthy and accessible.
        
        Returns:
            True if provider is healthy, False otherwise
        """
        try:
            return self.validate_credentials()
        except Exception:
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status information.
        
        Returns:
            Dictionary containing status information
        """
        return {
            "provider_name": self.config.provider_name,
            "provider_type": self.config.provider_type,
            "model_name": self.config.model_name,
            "is_healthy": self.is_healthy(),
            "credentials_valid": self.validate_credentials(),
            "provider_info": self.get_provider_info()
        }


class LLMProviderFactory:
    """
    Factory class for creating LLM providers.
    
    This factory handles the creation of different provider types
    and manages provider registrations.
    """
    
    _providers: Dict[str, type] = {}
    
    @classmethod
    def register_provider(cls, provider_type: str, provider_class: type) -> None:
        """Register a new provider type.
        
        Args:
            provider_type: Type identifier for the provider
            provider_class: Provider class to register
        """
        if not issubclass(provider_class, LLMProviderInterface):
            raise ValueError(f"Provider class must inherit from LLMProviderInterface")
        
        cls._providers[provider_type] = provider_class
    
    @classmethod
    def create_provider(cls, config: LLMProviderConfig) -> LLMProviderInterface:
        """Create a provider instance.
        
        Args:
            config: Provider configuration
            
        Returns:
            Provider instance
            
        Raises:
            ValueError: If provider type is not registered
        """
        provider_class = cls._providers.get(config.provider_type)
        if not provider_class:
            raise ValueError(f"Unknown provider type: {config.provider_type}")
        
        return provider_class(config)
    
    @classmethod
    def get_available_providers(cls) -> list:
        """Get list of available provider types.
        
        Returns:
            List of registered provider type names
        """
        return list(cls._providers.keys())
    
    @classmethod
    def is_provider_supported(cls, provider_type: str) -> bool:
        """Check if a provider type is supported.
        
        Args:
            provider_type: Provider type to check
            
        Returns:
            True if provider is supported, False otherwise
        """
        return provider_type in cls._providers
