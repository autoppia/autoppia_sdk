"""
Framework-Agnostic Language Model Providers for Autoppia SDK

This package provides interfaces and implementations for various language model providers
that are not tied to any specific framework (LangChain, OpenAI Assistants, LlamaIndex, etc.).
Each provider focuses on configuration management, credential validation, and framework adapter creation.

Quick Start:
    from autoppia.src.llms import LLMRegistry, LLMProviderConfig, create_openai_provider
    
    # Create provider configuration
    config = LLMProviderConfig(
        provider_name="my-openai",
        provider_type="openai",
        api_key="sk-...",
        model_name="gpt-4o"
    )
    
    # Register provider
    registry = LLMRegistry()
    registry.register_provider_from_config("openai", config)
    
    # Use with different frameworks
    langchain_llm = registry.create_framework_adapter("langchain", "openai")
    openai_client = registry.create_framework_adapter("openai_assistants", "openai")
"""

from .interface import LLMProviderInterface, LLMProviderConfig, LLMProviderFactory
from .providers import (
    OpenAIProvider,
    AnthropicProvider,
    GoogleGeminiProvider,
    CohereProvider,
    HuggingFaceProvider,
    OllamaProvider,
    LocalLLMProvider,
    # Convenience functions
    create_openai_provider,
    create_anthropic_provider,
    create_gemini_provider,
    create_cohere_provider,
    create_huggingface_provider,
    create_ollama_provider,
    create_local_provider
)
from .registry import LLMRegistry, get_llm_registry, register_provider, get_provider, create_framework_adapter

__all__ = [
    # Core interfaces
    "LLMProviderInterface",
    "LLMProviderConfig", 
    "LLMProviderFactory",
    
    # Provider implementations
    "OpenAIProvider",
    "AnthropicProvider",
    "GoogleGeminiProvider",
    "CohereProvider",
    "HuggingFaceProvider",
    "OllamaProvider",
    "LocalLLMProvider",
    
    # Registry
    "LLMRegistry",
    "get_llm_registry",
    "register_provider",
    "get_provider",
    "create_framework_adapter",
    
    # Convenience functions
    "create_openai_provider",
    "create_anthropic_provider",
    "create_gemini_provider",
    "create_cohere_provider",
    "create_huggingface_provider",
    "create_ollama_provider",
    "create_local_provider",
] 