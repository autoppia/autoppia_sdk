"""
Validation utilities for Autoppia SDK

This module provides common validation functions for API keys, URLs,
configuration objects, and other inputs.
"""

import re
from typing import Any, Dict, Optional
from urllib.parse import urlparse
from .exceptions import ValidationError


def validate_api_key(api_key: str, provider: Optional[str] = None) -> bool:
    """
    Validate an API key format.
    
    Args:
        api_key: The API key to validate
        provider: Optional provider name for provider-specific validation
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If the API key is invalid
    """
    if not api_key or not isinstance(api_key, str):
        raise ValidationError("API key must be a non-empty string")
    
    if len(api_key) < 10:
        raise ValidationError("API key must be at least 10 characters long")
    
    # Provider-specific validation
    if provider:
        if provider.lower() == "openai" and not api_key.startswith("sk-"):
            raise ValidationError("OpenAI API key must start with 'sk-'")
        elif provider.lower() == "anthropic" and not api_key.startswith("sk-ant-"):
            raise ValidationError("Anthropic API key must start with 'sk-ant-'")
    
    return True


def validate_url(url: str, schemes: Optional[list] = None) -> bool:
    """
    Validate a URL format.
    
    Args:
        url: The URL to validate
        schemes: Optional list of allowed schemes (default: ['http', 'https'])
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If the URL is invalid
    """
    if not url or not isinstance(url, str):
        raise ValidationError("URL must be a non-empty string")
    
    if schemes is None:
        schemes = ['http', 'https']
    
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValidationError("URL must have a valid scheme and netloc")
        
        if parsed.scheme not in schemes:
            raise ValidationError(f"URL scheme must be one of: {', '.join(schemes)}")
        
        return True
    except Exception as e:
        raise ValidationError(f"Invalid URL format: {e}")


def validate_config(config: Dict[str, Any], required_fields: Optional[list] = None) -> bool:
    """
    Validate a configuration dictionary.
    
    Args:
        config: Configuration dictionary to validate
        required_fields: Optional list of required field names
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If the configuration is invalid
    """
    if not isinstance(config, dict):
        raise ValidationError("Configuration must be a dictionary")
    
    if required_fields:
        for field in required_fields:
            if field not in config:
                raise ValidationError(f"Required field '{field}' is missing from configuration")
            if config[field] is None:
                raise ValidationError(f"Required field '{field}' cannot be None")
    
    return True


def validate_worker_config(config: Dict[str, Any]) -> bool:
    """
    Validate a worker configuration.
    
    Args:
        config: Worker configuration to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If the configuration is invalid
    """
    required_fields = ['name']
    
    # Basic validation
    validate_config(config, required_fields)
    
    # Name validation
    name = config.get('name')
    if not isinstance(name, str) or len(name.strip()) == 0:
        raise ValidationError("Worker name must be a non-empty string")
    
    # System prompt validation
    if 'system_prompt' in config and config['system_prompt'] is not None:
        if not isinstance(config['system_prompt'], str):
            raise ValidationError("System prompt must be a string")
    
    # Port validation
    if 'port' in config and config['port'] is not None:
        port = config['port']
        if not isinstance(port, int) or port < 1 or port > 65535:
            raise ValidationError("Port must be an integer between 1 and 65535")
    
    return True


def validate_llm_config(config: Dict[str, Any]) -> bool:
    """
    Validate an LLM configuration.
    
    Args:
        config: LLM configuration to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If the configuration is invalid
    """
    required_fields = ['api_key', 'provider']
    
    # Basic validation
    validate_config(config, required_fields)
    
    # API key validation
    validate_api_key(config['api_key'], config.get('provider'))
    
    # Provider validation
    provider = config['provider']
    if not isinstance(provider, str) or provider.lower() not in ['openai', 'anthropic']:
        raise ValidationError("Provider must be 'openai' or 'anthropic'")
    
    # Model validation
    if 'model' in config and config['model'] is not None:
        if not isinstance(config['model'], str):
            raise ValidationError("Model must be a string")
    
    return True


def validate_integration_config(config: Dict[str, Any]) -> bool:
    """
    Validate an integration configuration.
    
    Args:
        config: Integration configuration to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If the configuration is invalid
    """
    required_fields = ['type']
    
    # Basic validation
    validate_config(config, required_fields)
    
    # Type validation
    integration_type = config['type']
    if not isinstance(integration_type, str):
        raise ValidationError("Integration type must be a string")
    
    # Provider-specific validation
    if integration_type == 'web_search':
        if 'api_key' in config:
            validate_api_key(config['api_key'])
    elif integration_type == 'email':
        if 'smtp_server' in config:
            validate_url(config['smtp_server'], ['smtp', 'smtps'])
    elif integration_type == 'database':
        if 'connection_string' in config:
            # Basic connection string validation
            conn_str = config['connection_string']
            if not isinstance(conn_str, str) or len(conn_str.strip()) == 0:
                raise ValidationError("Database connection string must be a non-empty string")
    
    return True
