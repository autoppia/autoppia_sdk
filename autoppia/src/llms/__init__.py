"""
Language Model Services for Autoppia SDK

This package provides interfaces and implementations for various language model providers
including OpenAI, Anthropic, Google Gemini, Cohere, HuggingFace, Ollama, and local models.

Quick Start:
    from autoppia.src.llms import LLMRegistry, OpenAIService, GoogleGeminiService
    
    # Register and use OpenAI
    LLMRegistry.register_service("openai", OpenAIService)
    LLMRegistry.initialize_service("openai", api_key="your-key", model="gpt-4")
    
    # Register and use Google Gemini
    LLMRegistry.register_service("gemini", GoogleGeminiService)
    LLMRegistry.initialize_service("gemini", api_key="your-google-key", model="gemini-pro")
    
    # Get the service
    llm = LLMRegistry.get_service()
"""

from .interface import LLMServiceInterface
from .providers import (
    OpenAIService, 
    AnthropicService,
    GoogleGeminiService,
    CohereService,
    HuggingFaceService,
    OllamaService,
    LocalLLMService
)
from .registry import LLMRegistry
from .adapter import LLMAdapter

__all__ = [
    "LLMServiceInterface",
    "OpenAIService", 
    "AnthropicService",
    "GoogleGeminiService",
    "CohereService",
    "HuggingFaceService",
    "OllamaService",
    "LocalLLMService",
    "LLMRegistry",
    "LLMAdapter",
] 