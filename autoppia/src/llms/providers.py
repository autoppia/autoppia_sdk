"""
Framework-Agnostic LLM Providers for Autoppia SDK

This module provides implementations for various LLM providers that are not tied
to any specific framework. Each provider focuses on configuration management,
credential validation, and framework adapter creation.
"""

import os
import logging
from typing import Dict, Any, Optional
from .interface import LLMProviderInterface, LLMProviderConfig, LLMProviderFactory

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProviderInterface):
    """OpenAI LLM provider implementation.
    
    Supports OpenAI's GPT models with framework-agnostic configuration.
    """
    
    def _validate_config(self) -> None:
        """Validate OpenAI-specific configuration."""
        if not self.config.api_key.startswith("sk-"):
            raise ValueError("Invalid OpenAI API key format. Must start with 'sk-'")
        
        # Validate model name format
        valid_models = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
        if self.config.model_name not in valid_models:
            logger.warning(f"Model {self.config.model_name} may not be supported")
    
    def validate_credentials(self) -> bool:
        """Validate OpenAI API credentials."""
        try:
            # Simple validation - check if API key format is correct
            # In production, you might want to make a test API call
            return self.config.api_key.startswith("sk-") and len(self.config.api_key) > 20
        except Exception as e:
            logger.error(f"OpenAI credential validation failed: {e}")
            return False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get OpenAI provider information."""
        return {
            "provider": "OpenAI",
            "website": "https://openai.com",
            "api_docs": "https://platform.openai.com/docs",
            "supported_models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
            "features": ["chat", "completion", "embeddings", "assistants"]
        }
    
    def create_langchain_adapter(self) -> Any:
        """Create LangChain adapter for OpenAI."""
        try:
            from langchain_openai import ChatOpenAI
            
            return ChatOpenAI(
                model=self.config.model_name,
                openai_api_key=self.config.api_key,
                openai_api_base=self.config.api_base
            )
        except ImportError:
            raise ImportError("langchain-openai is required for LangChain adapter")
    
    def create_openai_assistants_adapter(self) -> Any:
        """Create OpenAI Assistants adapter."""
        try:
            from openai import OpenAI
            
            return OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.api_base
            )
        except ImportError:
            raise ImportError("openai is required for OpenAI Assistants adapter")


class AnthropicProvider(LLMProviderInterface):
    """Anthropic LLM provider implementation.
    
    Supports Anthropic's Claude models with framework-agnostic configuration.
    """
    
    def _validate_config(self) -> None:
        """Validate Anthropic-specific configuration."""
        if not self.config.api_key.startswith("sk-ant-"):
            raise ValueError("Invalid Anthropic API key format. Must start with 'sk-ant-'")
    
    def validate_credentials(self) -> bool:
        """Validate Anthropic API credentials."""
        try:
            return self.config.api_key.startswith("sk-ant-") and len(self.config.api_key) > 20
        except Exception as e:
            logger.error(f"Anthropic credential validation failed: {e}")
            return False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get Anthropic provider information."""
        return {
            "provider": "Anthropic",
            "website": "https://anthropic.com",
            "api_docs": "https://docs.anthropic.com",
            "supported_models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
            "features": ["chat", "completion", "vision"]
        }
    
    def create_langchain_adapter(self) -> Any:
        """Create LangChain adapter for Anthropic."""
        try:
            from langchain_anthropic import ChatAnthropic
            
            return ChatAnthropic(
                model=self.config.model_name,
                anthropic_api_key=self.config.api_key
            )
        except ImportError:
            raise ImportError("langchain-anthropic is required for LangChain adapter")


class GoogleGeminiProvider(LLMProviderInterface):
    """Google Gemini LLM provider implementation.
    
    Supports Google's Gemini models with framework-agnostic configuration.
    """
    
    def _validate_config(self) -> None:
        """Validate Google Gemini-specific configuration."""
        if not self.config.api_key.startswith("AIza"):
            raise ValueError("Invalid Google API key format. Must start with 'AIza'")
    
    def validate_credentials(self) -> bool:
        """Validate Google API credentials."""
        try:
            return self.config.api_key.startswith("AIza") and len(self.config.api_key) > 20
        except Exception as e:
            logger.error(f"Google Gemini credential validation failed: {e}")
            return False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get Google Gemini provider information."""
        return {
            "provider": "Google Gemini",
            "website": "https://ai.google.dev",
            "api_docs": "https://ai.google.dev/docs",
            "supported_models": ["gemini-pro", "gemini-pro-vision", "gemini-1.5-pro"],
            "features": ["chat", "completion", "vision", "multimodal"]
        }
    
    def create_langchain_adapter(self) -> Any:
        """Create LangChain adapter for Google Gemini."""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            
            return ChatGoogleGenerativeAI(
                model=self.config.model_name,
                google_api_key=self.config.api_key,
                convert_system_message_to_human=True
            )
        except ImportError:
            raise ImportError("langchain-google-genai is required for LangChain adapter")


class CohereProvider(LLMProviderInterface):
    """Cohere LLM provider implementation.
    
    Supports Cohere's language models with framework-agnostic configuration.
    """
    
    def _validate_config(self) -> None:
        """Validate Cohere-specific configuration."""
        # Cohere API keys don't have a specific prefix, just check length
        if len(self.config.api_key) < 10:
            raise ValueError("Invalid Cohere API key format")
    
    def validate_credentials(self) -> bool:
        """Validate Cohere API credentials."""
        try:
            return len(self.config.api_key) >= 10
        except Exception as e:
            logger.error(f"Cohere credential validation failed: {e}")
            return False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get Cohere provider information."""
        return {
            "provider": "Cohere",
            "website": "https://cohere.com",
            "api_docs": "https://docs.cohere.com",
            "supported_models": ["command", "command-light", "command-nightly"],
            "features": ["chat", "completion", "embeddings", "rerank"]
        }
    
    def create_langchain_adapter(self) -> Any:
        """Create LangChain adapter for Cohere."""
        try:
            from langchain_cohere import ChatCohere
            
            return ChatCohere(
                model=self.config.model_name,
                cohere_api_key=self.config.api_key
            )
        except ImportError:
            raise ImportError("langchain-cohere is required for LangChain adapter")


class HuggingFaceProvider(LLMProviderInterface):
    """HuggingFace LLM provider implementation.
    
    Supports HuggingFace models with framework-agnostic configuration.
    """
    
    def _validate_config(self) -> None:
        """Validate HuggingFace-specific configuration."""
        if not self.config.api_key.startswith("hf_"):
            raise ValueError("Invalid HuggingFace API key format. Must start with 'hf_'")
    
    def validate_credentials(self) -> bool:
        """Validate HuggingFace API credentials."""
        try:
            return self.config.api_key.startswith("hf_") and len(self.config.api_key) > 10
        except Exception as e:
            logger.error(f"HuggingFace credential validation failed: {e}")
            return False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get HuggingFace provider information."""
        return {
            "provider": "HuggingFace",
            "website": "https://huggingface.co",
            "api_docs": "https://huggingface.co/docs/api-inference",
            "supported_models": ["Any HuggingFace model"],
            "features": ["chat", "completion", "embeddings", "custom_models"]
        }
    
    def create_langchain_adapter(self) -> Any:
        """Create LangChain adapter for HuggingFace."""
        try:
            from langchain_huggingface import HuggingFaceEndpoint
            
            kwargs = {
                "huggingfacehub_api_token": self.config.api_key,
                "task": "text-generation"
            }
            
            if self.config.api_base:
                kwargs["endpoint_url"] = self.config.api_base
            
            return HuggingFaceEndpoint(**kwargs)
        except ImportError:
            raise ImportError("langchain-huggingface is required for LangChain adapter")


class OllamaProvider(LLMProviderInterface):
    """Ollama local LLM provider implementation.
    
    Supports local Ollama models with framework-agnostic configuration.
    """
    
    def _validate_config(self) -> None:
        """Validate Ollama-specific configuration."""
        # Ollama doesn't require API keys, just model names
        if not self.config.model_name:
            raise ValueError("Ollama model name is required")
    
    def validate_credentials(self) -> bool:
        """Validate Ollama configuration (no API key needed)."""
        try:
            # Check if Ollama server is accessible
            import requests
            base_url = self.config.api_base or "http://localhost:11434"
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama server not accessible: {e}")
            return False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get Ollama provider information."""
        return {
            "provider": "Ollama",
            "website": "https://ollama.ai",
            "api_docs": "https://github.com/ollama/ollama/blob/main/docs/api.md",
            "supported_models": ["llama2", "codellama", "mistral", "neural-chat"],
            "features": ["local_inference", "no_api_key", "custom_models"]
        }
    
    def create_langchain_adapter(self) -> Any:
        """Create LangChain adapter for Ollama."""
        try:
            from langchain_community.llms import Ollama
            
            return Ollama(
                model=self.config.model_name,
                base_url=self.config.api_base or "http://localhost:11434"
            )
        except ImportError:
            raise ImportError("langchain-community is required for LangChain adapter")


class LocalLLMProvider(LLMProviderInterface):
    """Local LLM provider implementation.
    
    Supports local models (Llama, GPT4All) with framework-agnostic configuration.
    """
    
    def _validate_config(self) -> None:
        """Validate local LLM-specific configuration."""
        if not self.config.provider_config or "model_path" not in self.config.provider_config:
            raise ValueError("Local LLM requires model_path in provider_config")
    
    def validate_credentials(self) -> bool:
        """Validate local LLM configuration."""
        try:
            model_path = self.config.provider_config.get("model_path")
            return model_path and os.path.exists(model_path)
        except Exception as e:
            logger.error(f"Local LLM validation failed: {e}")
            return False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get local LLM provider information."""
        return {
            "provider": "Local LLM",
            "website": "N/A",
            "api_docs": "N/A",
            "supported_models": ["llama", "gpt4all", "custom"],
            "features": ["offline_inference", "no_api_key", "full_control"]
        }
    
    def create_langchain_adapter(self) -> Any:
        """Create LangChain adapter for local LLM."""
        try:
            model_type = self.config.provider_config.get("model_type", "llama")
            model_path = self.config.provider_config.get("model_path")
            
            if model_type.lower() == "llama":
                from langchain_community.llms import LlamaCpp
                return LlamaCpp(
                    model_path=model_path,
                    n_ctx=2048,
                    n_threads=4
                )
            elif model_type.lower() == "gpt4all":
                from langchain_community.llms import GPT4All
                return GPT4All(
                    model=model_path,
                    n_threads=4
                )
            else:
                raise ValueError(f"Unsupported local model type: {model_type}")
        except ImportError:
            raise ImportError("langchain-community is required for LangChain adapter")


# Register all providers with the factory
LLMProviderFactory.register_provider("openai", OpenAIProvider)
LLMProviderFactory.register_provider("anthropic", AnthropicProvider)
LLMProviderFactory.register_provider("google", GoogleGeminiProvider)
LLMProviderFactory.register_provider("cohere", CohereProvider)
LLMProviderFactory.register_provider("huggingface", HuggingFaceProvider)
LLMProviderFactory.register_provider("ollama", OllamaProvider)
LLMProviderFactory.register_provider("local", LocalLLMProvider)


# Convenience functions for backward compatibility
def create_openai_provider(api_key: str, model: str = "gpt-4o", **kwargs) -> OpenAIProvider:
    """Create an OpenAI provider instance."""
    config = LLMProviderConfig(
        provider_name="openai",
        provider_type="openai",
        api_key=api_key,
        model_name=model,
        **kwargs
    )
    return OpenAIProvider(config)


def create_anthropic_provider(api_key: str, model: str = "claude-3-opus-20240229", **kwargs) -> AnthropicProvider:
    """Create an Anthropic provider instance."""
    config = LLMProviderConfig(
        provider_name="anthropic",
        provider_type="anthropic",
        api_key=api_key,
        model_name=model,
        **kwargs
    )
    return AnthropicProvider(config)


def create_gemini_provider(api_key: str, model: str = "gemini-pro", **kwargs) -> GoogleGeminiProvider:
    """Create a Google Gemini provider instance."""
    config = LLMProviderConfig(
        provider_name="gemini",
        provider_type="google",
        api_key=api_key,
        model_name=model,
        **kwargs
    )
    return GoogleGeminiProvider(config)


def create_cohere_provider(api_key: str, model: str = "command", **kwargs) -> CohereProvider:
    """Create a Cohere provider instance."""
    config = LLMProviderConfig(
        provider_name="cohere",
        provider_type="cohere",
        api_key=api_key,
        model_name=model,
        **kwargs
    )
    return CohereProvider(config)


def create_huggingface_provider(api_key: str, model: str, **kwargs) -> HuggingFaceProvider:
    """Create a HuggingFace provider instance."""
    config = LLMProviderConfig(
        provider_name="huggingface",
        provider_type="huggingface",
        api_key=api_key,
        model_name=model,
        **kwargs
    )
    return HuggingFaceProvider(config)


def create_ollama_provider(model: str = "llama2", base_url: str = "http://localhost:11434", **kwargs) -> OllamaProvider:
    """Create an Ollama provider instance."""
    config = LLMProviderConfig(
        provider_name="ollama",
        provider_type="ollama",
        api_key="",  # Ollama doesn't need API key
        model_name=model,
        api_base=base_url,
        **kwargs
    )
    return OllamaProvider(config)


def create_local_provider(model_path: str, model_type: str = "llama", **kwargs) -> LocalLLMProvider:
    """Create a local LLM provider instance."""
    config = LLMProviderConfig(
        provider_name="local",
        provider_type="local",
        api_key="",  # Local models don't need API key
        model_name=model_type,
        provider_config={"model_path": model_path, "model_type": model_type},
        **kwargs
    )
    return LocalLLMProvider(config) 