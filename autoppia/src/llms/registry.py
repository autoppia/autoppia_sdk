"""
Framework-Agnostic LLM Provider Registry for Autoppia SDK

This module provides a centralized registry for managing LLM providers
that is not tied to any specific framework implementation.
"""

import logging
from typing import Dict, Any, Optional, List
from .interface import LLMProviderInterface, LLMProviderConfig, LLMProviderFactory

logger = logging.getLogger(__name__)


class LLMRegistry:
    """
    Centralized registry for managing LLM providers.
    
    This registry allows developers to:
    1. Register and manage multiple LLM providers
    2. Switch between different frameworks (LangChain, OpenAI Assistants, etc.)
    3. Maintain provider configurations independently
    4. Access providers by name or type
    """
    
    _instance = None
    _providers: Dict[str, LLMProviderInterface] = {}
    _default_provider: Optional[str] = None
    
    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super(LLMRegistry, cls).__new__(cls)
        return cls._instance
    
    def register_provider(self, name: str, provider: LLMProviderInterface) -> None:
        """Register an LLM provider with a name.
        
        Args:
            name: Unique name for the provider
            provider: Provider instance to register
        """
        if not isinstance(provider, LLMProviderInterface):
            raise ValueError("Provider must implement LLMProviderInterface")
        
        self._providers[name] = provider
        logger.info(f"Registered LLM provider: {name} ({provider.config.provider_type})")
        
        # Set as default if it's the first one
        if self._default_provider is None:
            self._default_provider = name
    
    def register_provider_from_config(self, name: str, config: LLMProviderConfig) -> LLMProviderInterface:
        """Register a provider using configuration.
        
        Args:
            name: Unique name for the provider
            config: Provider configuration
            
        Returns:
            Created provider instance
        """
        provider = LLMProviderFactory.create_provider(config)
        self.register_provider(name, provider)
        return provider
    
    def get_provider(self, name: Optional[str] = None) -> Optional[LLMProviderInterface]:
        """Get a provider by name.
        
        Args:
            name: Provider name (uses default if None)
            
        Returns:
            Provider instance or None if not found
        """
        provider_name = name or self._default_provider
        if not provider_name:
            logger.warning("No default provider set")
            return None
        
        provider = self._providers.get(provider_name)
        if not provider:
            logger.warning(f"Provider '{provider_name}' not found")
            return None
        
        return provider
    
    def get_provider_by_type(self, provider_type: str) -> Optional[LLMProviderInterface]:
        """Get the first provider of a specific type.
        
        Args:
            provider_type: Type of provider to find
            
        Returns:
            Provider instance or None if not found
        """
        for provider in self._providers.values():
            if provider.config.provider_type == provider_type:
                return provider
        return None
    
    def list_providers(self) -> List[Dict[str, Any]]:
        """List all registered providers with their information.
        
        Returns:
            List of provider information dictionaries
        """
        providers_info = []
        for name, provider in self._providers.items():
            info = {
                "name": name,
                "type": provider.config.provider_type,
                "model": provider.config.model_name,
                "is_healthy": provider.is_healthy(),
                "is_default": (name == self._default_provider)
            }
            providers_info.append(info)
        return providers_info
    
    def set_default_provider(self, name: str) -> bool:
        """Set the default provider.
        
        Args:
            name: Name of the provider to set as default
            
        Returns:
            True if successful, False if provider not found
        """
        if name not in self._providers:
            logger.error(f"Cannot set default provider: '{name}' not found")
            return False
        
        self._default_provider = name
        logger.info(f"Set default provider to: {name}")
        return True
    
    def remove_provider(self, name: str) -> bool:
        """Remove a provider from the registry.
        
        Args:
            name: Name of the provider to remove
            
        Returns:
            True if successful, False if provider not found
        """
        if name not in self._providers:
            return False
        
        # Don't allow removing the default provider if it's the only one
        if len(self._providers) == 1:
            logger.warning("Cannot remove the last provider")
            return False
        
        removed_provider = self._providers.pop(name)
        logger.info(f"Removed provider: {name}")
        
        # Update default provider if necessary
        if name == self._default_provider:
            # Set first available provider as default
            self._default_provider = next(iter(self._providers.keys()))
            logger.info(f"Updated default provider to: {self._default_provider}")
        
        return True
    
    def clear_providers(self) -> None:
        """Clear all registered providers."""
        self._providers.clear()
        self._default_provider = None
        logger.info("Cleared all LLM providers")
    
    def get_provider_status(self, name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get comprehensive status of a provider.
        
        Args:
            name: Provider name (uses default if None)
            
        Returns:
            Provider status dictionary or None if not found
        """
        provider = self.get_provider(name)
        if not provider:
            return None
        
        status = provider.get_status()
        status["registry_name"] = name or self._default_provider
        status["is_default"] = (name or self._default_provider) == self._default_provider
        return status
    
    def validate_all_providers(self) -> Dict[str, bool]:
        """Validate all registered providers.
        
        Returns:
            Dictionary mapping provider names to validation status
        """
        validation_results = {}
        for name, provider in self._providers.items():
            try:
                is_valid = provider.validate_credentials()
                validation_results[name] = is_valid
                logger.info(f"Provider '{name}' validation: {'✅' if is_valid else '❌'}")
            except Exception as e:
                validation_results[name] = False
                logger.error(f"Provider '{name}' validation failed: {e}")
        
        return validation_results
    
    def get_available_frameworks(self, name: Optional[str] = None) -> List[str]:
        """Get available frameworks for a provider.
        
        Args:
            name: Provider name (uses default if None)
            
        Returns:
            List of available framework names
        """
        provider = self.get_provider(name)
        if not provider:
            return []
        
        frameworks = []
        
        # Check which framework adapters are available
        try:
            provider.create_langchain_adapter()
            frameworks.append("langchain")
        except (ImportError, NotImplementedError):
            pass
        
        try:
            provider.create_openai_assistants_adapter()
            frameworks.append("openai_assistants")
        except (ImportError, NotImplementedError):
            pass
        
        try:
            provider.create_llamaindex_adapter()
            frameworks.append("llamaindex")
        except (ImportError, NotImplementedError):
            pass
        
        return frameworks
    
    def create_framework_adapter(self, framework: str, name: Optional[str] = None, **kwargs) -> Any:
        """Create a framework-specific adapter for a provider.
        
        Args:
            framework: Framework name (langchain, openai_assistants, llamaindex)
            name: Provider name (uses default if None)
            **kwargs: Additional framework-specific arguments
            
        Returns:
            Framework-specific adapter instance
            
        Raises:
            ValueError: If framework is not supported
            NotImplementedError: If adapter creation fails
        """
        provider = self.get_provider(name)
        if not provider:
            raise ValueError(f"Provider '{name or 'default'}' not found")
        
        framework = framework.lower()
        
        if framework == "langchain":
            return provider.create_langchain_adapter()
        elif framework == "openai_assistants":
            return provider.create_openai_assistants_adapter()
        elif framework == "llamaindex":
            return provider.create_llamaindex_adapter()
        else:
            return provider.create_custom_adapter(framework, **kwargs)
    
    def get_registry_info(self) -> Dict[str, Any]:
        """Get comprehensive registry information.
        
        Returns:
            Dictionary containing registry status and information
        """
        return {
            "total_providers": len(self._providers),
            "default_provider": self._default_provider,
            "available_provider_types": list(set(p.config.provider_type for p in self._providers.values())),
            "providers": self.list_providers(),
            "factory_supported_types": LLMProviderFactory.get_available_providers()
        }


# Global registry instance
def get_llm_registry() -> LLMRegistry:
    """Get the global LLM registry instance."""
    return LLMRegistry()


# Convenience functions for backward compatibility
def register_provider(name: str, provider: LLMProviderInterface) -> None:
    """Register a provider with the global registry."""
    get_llm_registry().register_provider(name, provider)


def get_provider(name: Optional[str] = None) -> Optional[LLMProviderInterface]:
    """Get a provider from the global registry."""
    return get_llm_registry().get_provider(name)


def create_framework_adapter(framework: str, name: Optional[str] = None, **kwargs) -> Any:
    """Create a framework adapter from the global registry."""
    return get_llm_registry().create_framework_adapter(framework, name, **kwargs) 