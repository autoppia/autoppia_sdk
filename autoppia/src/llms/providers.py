"""
Simple LLM Provider Configuration for Autoppia SDK

This module provides a simplified, framework-agnostic way to configure LLM providers.
It focuses on basic provider information and configuration without creating specific LLM instances.
"""

import os
import logging
from typing import Dict, Any, Optional
from .interface import LLMProvider, LLMConfig

logger = logging.getLogger(__name__)


class SimpleLLMProvider(LLMProvider):
    """Simple LLM provider implementation.
    
    A generic provider that works with any LLM service by providing
    basic configuration and validation without framework-specific implementations.
    """
    
    def _validate_config(self) -> None:
        """Validate basic configuration."""
        if not self.config.api_key:
            raise ValueError("API key is required")
        if not self.config.model_name:
            raise ValueError("Model name is required")
        if not self.config.provider_type:
            raise ValueError("Provider type is required")


# Convenience function to create a simple provider
def create_provider(
    provider_type: str,
    api_key: str,
    model_name: str,
    provider_name: str = None,
    api_base: str = None,
    provider_config: Dict[str, Any] = None,
    **kwargs
) -> SimpleLLMProvider:
    """Create a simple LLM provider instance.
    
    Args:
        provider_type: Type of provider (e.g., "openai", "anthropic", "custom")
        api_key: API key for the provider
        model_name: Name of the model to use
        provider_name: Optional custom name for the provider
        api_base: Optional custom API base URL
        provider_config: Optional additional provider-specific configuration
        **kwargs: Additional configuration options
    
    Returns:
        SimpleLLMProvider: Configured provider instance
    """
    config = LLMConfig(
        provider_name=provider_name or provider_type,
        provider_type=provider_type,
        api_key=api_key,
        model_name=model_name,
        api_base=api_base,
        provider_config=provider_config or {},
        **kwargs
    )
    return SimpleLLMProvider(config)


# Common provider presets for convenience
def create_openai_provider(api_key: str, model: str = "gpt-4o", **kwargs) -> SimpleLLMProvider:
    """Create an OpenAI provider configuration."""
    return create_provider(
        provider_type="openai",
        api_key=api_key,
        model_name=model,
        provider_name="OpenAI",
        **kwargs
    )


def create_anthropic_provider(api_key: str, model: str = "claude-3-opus-20240229", **kwargs) -> SimpleLLMProvider:
    """Create an Anthropic provider configuration."""
    return create_provider(
        provider_type="anthropic",
        api_key=api_key,
        model_name=model,
        provider_name="Anthropic",
        **kwargs
    )


def create_custom_provider(
    provider_type: str,
    api_key: str,
    model_name: str,
    api_base: str = None,
    **kwargs
) -> SimpleLLMProvider:
    """Create a custom provider configuration."""
    return create_provider(
        provider_type=provider_type,
        api_key=api_key,
        model_name=model_name,
        provider_name=f"Custom {provider_type.title()}",
        api_base=api_base,
        **kwargs
    )


def create_local_provider(
    model_name: str,
    model_path: str = None,
    base_url: str = "http://localhost:11434",
    **kwargs
) -> SimpleLLMProvider:
    """Create a local provider configuration."""
    provider_config = {}
    if model_path:
        provider_config["model_path"] = model_path
    
    return create_provider(
        provider_type="local",
        api_key="",  # Local models don't need API key
        model_name=model_name,
        provider_name="Local LLM",
        api_base=base_url,
        provider_config=provider_config,
        **kwargs
    )