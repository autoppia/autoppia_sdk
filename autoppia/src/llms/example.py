"""
Simple LLM Configuration Example

This example demonstrates how to use the simplified LLM configuration system.
"""

from .interface import LLMConfig
from .providers import create_openai_provider, create_anthropic_provider, create_custom_provider
from .registry import LLMRegistry


def basic_config_example():
    """Example of basic LLM configuration."""
    print("=== Basic LLM Configuration Example ===")
    
    # Create a simple OpenAI configuration
    openai_config = create_openai_provider(
        api_key="sk-your-openai-key-here",
        model="gpt-4o"
    )
    
    # Get configuration information
    info = openai_config.get_info()
    print(f"Provider: {info['provider_type']}")
    print(f"Model: {info['model_name']}")
    print(f"Has API Key: {info['has_api_key']}")
    print(f"Custom Base URL: {info['custom_base_url']}")
    print()


def registry_example():
    """Example of using the LLM registry."""
    print("=== LLM Registry Example ===")
    
    # Create registry
    registry = LLMRegistry()
    
    # Add multiple configurations
    openai_config = create_openai_provider(
        api_key="sk-your-openai-key-here",
        model="gpt-4o"
    )
    
    anthropic_config = create_anthropic_provider(
        api_key="sk-ant-your-anthropic-key-here",
        model="claude-3-opus-20240229"
    )
    
    custom_config = create_custom_provider(
        provider_type="my_custom_llm",
        api_key="my-api-key",
        model_name="my-model",
        api_base="https://my-api.com"
    )
    
    # Add to registry
    registry.add_config("openai-main", openai_config)
    registry.add_config("anthropic-main", anthropic_config)
    registry.add_config("custom-llm", custom_config)
    
    # Set default
    registry.set_default_config("openai-main")
    
    # List all configurations
    configs = registry.list_configs()
    print("Available configurations:")
    for config in configs:
        default_marker = " (default)" if config['is_default'] else ""
        print(f"  - {config['name']}: {config['type']} - {config['model']}{default_marker}")
    
    # Get registry info
    registry_info = registry.get_registry_info()
    print(f"\nTotal configurations: {registry_info['total_configs']}")
    print(f"Default configuration: {registry_info['default_config']}")
    print(f"Available provider types: {', '.join(registry_info['available_provider_types'])}")
    print()


def custom_provider_example():
    """Example of creating custom provider configurations."""
    print("=== Custom Provider Example ===")
    
    # Create a local Ollama configuration
    local_config = create_custom_provider(
        provider_type="ollama",
        api_key="",  # No API key needed for local
        model_name="llama2",
        api_base="http://localhost:11434"
    )
    
    # Create a custom API configuration
    custom_api_config = create_custom_provider(
        provider_type="custom_api",
        api_key="my-secret-key",
        model_name="gpt-4-clone",
        api_base="https://my-llm-api.com/v1",
        provider_config={
            "temperature": 0.7,
            "max_tokens": 1000,
            "custom_headers": {"X-Custom-Header": "value"}
        }
    )
    
    print("Local Ollama config:")
    print(f"  - {local_config.get_info()}")
    print()
    
    print("Custom API config:")
    print(f"  - {custom_api_config.get_info()}")
    print()


if __name__ == "__main__":
    basic_config_example()
    registry_example()
    custom_provider_example() 