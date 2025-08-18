# Framework-Agnostic LLM Configuration Guide

This guide explains how to configure and use different Language Model providers in the Autoppia SDK
using the new framework-agnostic system that is not tied to any specific framework implementation.

## 🚀 Quick Start

```python
from autoppia.src.llms import LLMRegistry, LLMProviderConfig, create_openai_provider

# Create provider configuration
config = LLMProviderConfig(
    provider_name="my-openai",
    provider_type="openai",
    api_key="sk-...",
    model_name="gpt-4o"
)

# Register and use
registry = LLMRegistry()
registry.register_provider_from_config("openai", config)

# Use with different frameworks
langchain_llm = registry.create_framework_adapter("langchain", "openai")
openai_client = registry.create_framework_adapter("openai_assistants", "openai")
```

## 🔑 Supported LLM Providers

### 1. OpenAI
```python
from autoppia.src.llms import create_openai_provider

provider = create_openai_provider(
    api_key="sk-...",  # Your OpenAI API key
    model="gpt-4o"     # Model name
)

# Available models: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo
```

**Environment Variable**: `OPENAI_API_KEY`

### 2. Google Gemini
```python
from autoppia.src.llms import create_gemini_provider

provider = create_gemini_provider(
    api_key="AIza...",  # Your Google AI API key
    model="gemini-pro"   # Model name
)

# Available models: gemini-pro, gemini-pro-vision, gemini-1.5-pro
```

**Environment Variable**: `GOOGLE_API_KEY`

### 3. Anthropic Claude
```python
from autoppia.src.llms import create_anthropic_provider

provider = create_anthropic_provider(
    api_key="sk-ant-...",  # Your Anthropic API key
    model="claude-3-opus-20240229"  # Model name
)

# Available models: claude-3-opus-20240229, claude-3-sonnet-20240229, claude-3-haiku-20240307
```

**Environment Variable**: `ANTHROPIC_API_KEY`

### 4. Cohere
```python
from autoppia.src.llms import create_cohere_provider

provider = create_cohere_provider(
    api_key="...",  # Your Cohere API key
    model="command"  # Model name
)

# Available models: command, command-light, command-nightly
```

**Environment Variable**: `COHERE_API_KEY`

### 5. HuggingFace
```python
from autoppia.src.llms import create_huggingface_provider

provider = create_huggingface_provider(
    api_key="hf_...",  # Your HuggingFace API key
    model="meta-llama/Llama-2-7b-chat-hf"  # Model name
)

# Popular models: meta-llama/Llama-2-7b-chat-hf, microsoft/DialoGPT-medium
```

**Environment Variable**: `HUGGINGFACE_API_KEY`

### 6. Ollama (Local)
```python
from autoppia.src.llms import create_ollama_provider

provider = create_ollama_provider(
    model="llama2",  # Model name
    base_url="http://localhost:11434"  # Ollama server URL
)

# Available models: llama2, codellama, mistral, neural-chat
# Requires Ollama to be running locally
```

### 7. Local Models
```python
from autoppia.src.llms import create_local_provider

# Llama model
llama_provider = create_local_provider(
    model_path="/path/to/llama-2-7b.gguf",
    model_type="llama"
)

# GPT4All model
gpt4all_provider = create_local_provider(
    model_path="/path/to/gpt4all-model.bin",
    model_type="gpt4all"
)
```

## 🔄 Using Multiple Providers

```python
from autoppia.src.workers import WorkerConfig
from autoppia.src.llms import create_openai_provider, create_gemini_provider

# Create providers
openai_provider = create_openai_provider(api_key="sk-...", model="gpt-4o")
gemini_provider = create_gemini_provider(api_key="AIza...", model="gemini-pro")

# Register in registry
registry = LLMRegistry()
registry.register_provider("openai", openai_provider)
registry.register_provider("gemini", gemini_provider)

# Switch between providers
registry.set_default_provider("gemini")
gemini_llm = registry.create_framework_adapter("langchain", "gemini")
```

## ⚙️ Environment Variables

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Google Gemini
export GOOGLE_API_KEY="AIza..."

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# Cohere
export COHERE_API_KEY="..."

# HuggingFace
export HUGGINGFACE_API_KEY="hf_..."
```

## 🏗️ Framework Adapters

### LangChain
```python
# Create LangChain adapter
langchain_llm = provider.create_langchain_adapter()
response = langchain_llm.predict("Hello!")
```

### OpenAI Assistants
```python
# Create OpenAI Assistants adapter
openai_client = provider.create_openai_assistants_adapter()
# Use for OpenAI Assistants API
```

### LlamaIndex
```python
# Create LlamaIndex adapter
llamaindex_llm = provider.create_llamaindex_adapter()
# Use for LlamaIndex workflows
```

### Custom Frameworks
```python
# Create custom framework adapter
custom_adapter = provider.create_custom_adapter("my_framework", **kwargs)
```

## 🧪 Testing Providers

```python
def check_provider_health(provider):
    """Check if an LLM provider is working."""
    try:
        is_healthy = provider.is_healthy()
        credentials_valid = provider.validate_credentials()
        return is_healthy and credentials_valid
    except Exception as e:
        return False

# Test all providers
for name, provider in providers.items():
    is_healthy = check_provider_health(provider)
    print(f"{name}: {'✅' if is_healthy else '❌'}")
```

## 📚 Examples

See `autoppia/examples/framework_agnostic_llm.py` for a complete working example.

## 🔧 Advanced Configuration

### Provider Factory
```python
from autoppia.src.llms import LLMProviderFactory, LLMProviderConfig

# Create config
config = LLMProviderConfig(
    provider_name="custom",
    provider_type="openai",
    api_key="sk-...",
    model_name="gpt-4o"
)

# Create provider via factory
provider = LLMProviderFactory.create_provider(config)
```

### Registry Management
```python
registry = LLMRegistry()

# List all providers
providers = registry.list_providers()

# Get provider status
status = registry.get_provider_status("openai")

# Validate all providers
validation = registry.validate_all_providers()

# Get available frameworks
frameworks = registry.get_available_frameworks("openai")
```
