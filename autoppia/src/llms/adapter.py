"""
Simple LLM Configuration Adapter for Autoppia SDK

This module provides a simple adapter for converting backend LLM configuration
into the simplified LLMConfig format.
"""

from .interface import LLMConfig


class LLMAdapter:
    """Simple adapter for converting backend LLM configuration.
    
    This class handles the conversion of backend LLM configuration into
    the simplified LLMConfig format.
    """

    @staticmethod
    def from_backend_config(backend_config: dict) -> LLMConfig:
        """Convert backend configuration to LLMConfig.
        
        Args:
            backend_config: Backend LLM configuration dictionary
            
        Returns:
            LLMConfig: Simplified configuration object
            
        Raises:
            ValueError: If required configuration is missing
        """
        # Extract basic information from backend config
        provider_type = backend_config.get("provider_type", "").lower()
        api_key = backend_config.get("api_key", "")
        model_name = backend_config.get("model_name", "")
        provider_name = backend_config.get("provider_name", provider_type)
        
        # Validate required fields
        if not api_key:
            raise ValueError(f"Missing API key for {provider_type} provider")
        if not model_name:
            raise ValueError(f"Missing model name for {provider_type} provider")
        if not provider_type:
            raise ValueError("Missing provider type")
        
        # Create simplified config
        return LLMConfig(
            provider_name=provider_name,
            provider_type=provider_type,
            api_key=api_key,
            model_name=model_name,
            api_base=backend_config.get("api_base"),
            provider_config=backend_config.get("provider_config", {})
        )
    
    @staticmethod
    def to_backend_config(config: LLMConfig) -> dict:
        """Convert LLMConfig to backend configuration format.
        
        Args:
            config: LLMConfig object
            
        Returns:
            dict: Backend configuration format
        """
        return {
            "provider_type": config.provider_type.upper(),
            "provider_name": config.provider_name,
            "api_key": config.api_key,
            "model_name": config.model_name,
            "api_base": config.api_base,
            "provider_config": config.provider_config or {}
        }
