"""
Simple LLM Configuration for Autoppia SDK

This package provides a simple, clean interface for LLM configuration
without framework-specific implementations or complex abstractions.

Quick Start:
    from autoppia.src.llms import LLMConfig, create_openai_provider, LLMRegistry
    
    # Create provider configuration
    config = create_openai_provider(
        api_key="sk-...",
        model="gpt-4o"
    )
    
    # Add to registry
    registry = LLMRegistry()
    registry.add_config("my-openai", config)
    
    # Get configuration info
    info = config.get_info()
    print(f"Provider: {info['provider_type']}, Model: {info['model_name']}")
"""

from .interface import LLMConfig, LLMProvider
from .providers import (
    SimpleLLMProvider,
    # Convenience functions
    create_provider,
    create_openai_provider,
    create_anthropic_provider,
    create_custom_provider,
    create_local_provider
)
from .registry import LLMRegistry, get_llm_registry, add_llm_config, get_llm_config, list_llm_configs
from .adapter import LLMAdapter

__all__ = [
    # Core classes
    "LLMConfig",
    "LLMProvider",
    "SimpleLLMProvider",
    
    # Registry
    "LLMRegistry",
    "get_llm_registry",
    "add_llm_config",
    "get_llm_config",
    "list_llm_configs",
    
    # Convenience functions
    "create_provider",
    "create_openai_provider",
    "create_anthropic_provider",
    "create_custom_provider",
    "create_local_provider",
    
    # Adapter
    "LLMAdapter",
] 