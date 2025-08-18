"""
Framework-Agnostic LLM Usage Example

This example demonstrates how to use the Autoppia SDK's framework-agnostic LLM system
to work with different frameworks like LangChain, OpenAI Assistants, and LlamaIndex
without being tied to any specific implementation.
"""

import asyncio
import logging
from typing import Dict, Any
from autoppia.src.llms import (
    LLMRegistry,
    LLMProviderConfig,
    create_openai_provider,
    create_gemini_provider,
    create_anthropic_provider
)

logger = logging.getLogger(__name__)


def demonstrate_framework_agnostic_llm():
    """Demonstrate the framework-agnostic LLM system."""
    
    print("🚀 Framework-Agnostic LLM System Demo")
    print("=" * 50)
    
    # 1. Create LLM providers with configuration
    print("\n1️⃣ Creating LLM Providers...")
    
    # OpenAI provider
    openai_provider = create_openai_provider(
        api_key="sk-your-openai-key",
        model="gpt-4o"
    )
    
    # Google Gemini provider
    gemini_provider = create_gemini_provider(
        api_key="AIza-your-google-key",
        model="gemini-pro"
    )
    
    # Anthropic provider
    anthropic_provider = create_anthropic_provider(
        api_key="sk-ant-your-anthropic-key",
        model="claude-3-opus-20240229"
    )
    
    print(f"✅ Created providers: OpenAI, Gemini, Anthropic")
    
    # 2. Register providers in the registry
    print("\n2️⃣ Registering Providers in Registry...")
    
    registry = LLMRegistry()
    
    registry.register_provider("openai", openai_provider)
    registry.register_provider("gemini", gemini_provider)
    registry.register_provider("anthropic", anthropic_provider)
    
    print(f"✅ Registered {len(registry.list_providers())} providers")
    
    # 3. Show provider information
    print("\n3️⃣ Provider Information...")
    
    for provider_info in registry.list_providers():
        print(f"  📋 {provider_info['name']}: {provider_info['type']} ({provider_info['model']})")
        print(f"     Health: {'✅' if provider_info['is_healthy'] else '❌'}")
        print(f"     Default: {'⭐' if provider_info['is_default'] else ''}")
    
    # 4. Demonstrate framework adapters
    print("\n4️⃣ Framework Adapters...")
    
    # Check available frameworks for each provider
    for provider_name in ["openai", "gemini", "anthropic"]:
        frameworks = registry.get_available_frameworks(provider_name)
        print(f"  🔌 {provider_name}: {', '.join(frameworks) if frameworks else 'None'}")
    
    # 5. Create and use framework adapters
    print("\n5️⃣ Using Framework Adapters...")
    
    try:
        # LangChain adapter
        print("  📚 Creating LangChain adapter...")
        langchain_llm = registry.create_framework_adapter("langchain", "openai")
        print(f"     ✅ LangChain LLM created: {type(langchain_llm).__name__}")
        
        # OpenAI Assistants adapter
        print("  🤖 Creating OpenAI Assistants adapter...")
        openai_client = registry.create_framework_adapter("openai_assistants", "openai")
        print(f"     ✅ OpenAI client created: {type(openai_client).__name__}")
        
    except ImportError as e:
        print(f"     ⚠️  Framework not available: {e}")
    except Exception as e:
        print(f"     ❌ Error creating adapter: {e}")
    
    # 6. Provider health and validation
    print("\n6️⃣ Provider Health Check...")
    
    validation_results = registry.validate_all_providers()
    for provider_name, is_valid in validation_results.items():
        status = "✅ Healthy" if is_valid else "❌ Unhealthy"
        print(f"  {provider_name}: {status}")
    
    # 7. Registry information
    print("\n7️⃣ Registry Information...")
    
    registry_info = registry.get_registry_info()
    print(f"  📊 Total providers: {registry_info['total_providers']}")
    print(f"  🎯 Default provider: {registry_info['default_provider']}")
    print(f"  🔧 Supported types: {', '.join(registry_info['available_provider_types'])}")
    
    return registry


def demonstrate_provider_configuration():
    """Demonstrate different ways to configure LLM providers."""
    
    print("\n🔧 Provider Configuration Examples")
    print("=" * 40)
    
    # Method 1: Using convenience functions
    print("\n1️⃣ Convenience Functions:")
    
    openai_provider = create_openai_provider(
        api_key="sk-your-key",
        model="gpt-4o",
        api_base="https://api.openai.com/v1"
    )
    print(f"  ✅ OpenAI provider created with model: {openai_provider.config.model_name}")
    
    # Method 2: Using configuration objects
    print("\n2️⃣ Configuration Objects:")
    
    config = LLMProviderConfig(
        provider_name="custom-gemini",
        provider_type="google",
        api_key="AIza-your-key",
        model_name="gemini-pro",
        preferred_framework="langchain"
    )
    print(f"  ✅ Custom config created: {config.provider_name}")
    
    # Method 3: Provider factory
    print("\n3️⃣ Provider Factory:")
    
    from autoppia.src.llms import LLMProviderFactory
    
    if LLMProviderFactory.is_provider_supported("google"):
        provider = LLMProviderFactory.create_provider(config)
        print(f"  ✅ Provider created via factory: {provider.config.provider_name}")
    
    # Method 4: Environment-based configuration
    print("\n4️⃣ Environment-Based Configuration:")
    
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    env_config = LLMProviderConfig(
        provider_name="env-openai",
        provider_type="openai",
        api_key=os.getenv("OPENAI_API_KEY", ""),
        model_name=os.getenv("OPENAI_MODEL", "gpt-4o")
    )
    print(f"  ✅ Environment config created: {env_config.provider_name}")


def demonstrate_framework_switching():
    """Demonstrate switching between different frameworks."""
    
    print("\n🔄 Framework Switching Demo")
    print("=" * 35)
    
    # Create a provider
    provider = create_openai_provider(
        api_key="sk-your-key",
        model="gpt-4o"
    )
    
    # Test different framework adapters
    frameworks = ["langchain", "openai_assistants"]
    
    for framework in frameworks:
        try:
            print(f"\n🔌 Testing {framework} adapter...")
            
            if framework == "langchain":
                adapter = provider.create_langchain_adapter()
                print(f"  ✅ LangChain adapter created: {type(adapter).__name__}")
                
                # Test basic functionality
                try:
                    response = adapter.predict("Hello, how are you?")
                    print(f"  💬 Response: {response[:100]}...")
                except Exception as e:
                    print(f"  ⚠️  LangChain test failed: {e}")
                    
            elif framework == "openai_assistants":
                adapter = provider.create_openai_assistants_adapter()
                print(f"  ✅ OpenAI Assistants adapter created: {type(adapter).__name__}")
                
                # Test basic functionality
                try:
                    # This would require actual API calls, so we just show the client
                    print(f"  🔑 Client ready for API calls")
                except Exception as e:
                    print(f"  ⚠️  OpenAI Assistants test failed: {e}")
                    
        except ImportError as e:
            print(f"  ❌ Framework not available: {e}")
        except Exception as e:
            print(f"  ❌ Adapter creation failed: {e}")


def demonstrate_advanced_usage():
    """Demonstrate advanced usage patterns."""
    
    print("\n🚀 Advanced Usage Patterns")
    print("=" * 35)
    
    # Create multiple providers
    providers = {
        "openai": create_openai_provider("sk-your-key", "gpt-4o"),
        "gemini": create_gemini_provider("AIza-your-key", "gemini-pro"),
        "anthropic": create_anthropic_provider("sk-ant-your-key", "claude-3-opus")
    }
    
    # Register all providers
    registry = LLMRegistry()
    for name, provider in providers.items():
        registry.register_provider(name, provider)
    
    # Demonstrate provider switching
    print("\n1️⃣ Provider Switching:")
    
    test_message = "What is the capital of France?"
    
    for provider_name in ["openai", "gemini", "anthropic"]:
        print(f"\n  🔄 Switching to {provider_name}...")
        
        # Set as default
        registry.set_default_provider(provider_name)
        
        # Get provider status
        status = registry.get_provider_status(provider_name)
        print(f"     Status: {status['is_healthy']}")
        
        # Try to create a LangChain adapter
        try:
            llm = registry.create_framework_adapter("langchain", provider_name)
            print(f"     ✅ {provider_name} LangChain adapter ready")
        except Exception as e:
            print(f"     ❌ {provider_name} adapter failed: {e}")
    
    # Demonstrate provider management
    print("\n2️⃣ Provider Management:")
    
    # List all providers
    all_providers = registry.list_providers()
    print(f"  📋 Total providers: {len(all_providers)}")
    
    # Remove a provider
    if "anthropic" in [p["name"] for p in all_providers]:
        registry.remove_provider("anthropic")
        print(f"  🗑️  Removed anthropic provider")
    
    # Show updated list
    updated_providers = registry.list_providers()
    print(f"  📋 Remaining providers: {len(updated_providers)}")
    
    # Clear all providers
    registry.clear_providers()
    print(f"  🧹 Cleared all providers")


async def main():
    """Main demonstration function."""
    
    try:
        # Basic framework-agnostic demo
        registry = demonstrate_framework_agnostic_llm()
        
        # Provider configuration examples
        demonstrate_provider_configuration()
        
        # Framework switching demo
        demonstrate_framework_switching()
        
        # Advanced usage patterns
        demonstrate_advanced_usage()
        
        print("\n🎉 Framework-Agnostic LLM Demo Completed!")
        print("\n💡 Key Benefits:")
        print("  • No framework lock-in")
        print("  • Easy switching between providers")
        print("  • Consistent configuration interface")
        print("  • Framework adapter creation")
        print("  • Provider health monitoring")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        logger.error(f"Demo execution failed: {e}")


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(main())
