# LLM Configuration Guide

This guide explains how to configure and use different Language Model providers in the Autoppia SDK.

## 🚀 Quick Start

```python
from autoppia.src.llms import LLMRegistry, OpenAIService, GoogleGeminiService

# Register services
LLMRegistry.register_service("openai", OpenAIService)
LLMRegistry.register_service("gemini", GoogleGeminiService)

# Initialize and use
LLMRegistry.initialize_service("openai", api_key="your-key", model="gpt-4")
llm = LLMRegistry.get_service()
response = llm.predict("Hello!")
```

## 🔑 Supported LLM Providers

### 1. OpenAI
```python
from autoppia.src.llms import OpenAIService

service = OpenAIService(
    api_key="sk-...",  # Your OpenAI API key
    model="gpt-4o"     # Model name
)
```

### 2. Google Gemini
```python
from autoppia.src.llms import GoogleGeminiService

service = GoogleGeminiService(
    api_key="AIza...",  # Your Google AI API key
    model="gemini-pro"   # Model name
)
```

### 3. Anthropic Claude
```python
from autoppia.src.llms import AnthropicService

service = AnthropicService(
    api_key="sk-ant-...",  # Your Anthropic API key
    model="claude-3-opus-20240229"  # Model name
)
```

### 4. Cohere
```python
from autoppia.src.llms import CohereService

service = CohereService(
    api_key="...",  # Your Cohere API key
    model="command"  # Model name
)
```

### 5. HuggingFace
```python
from autoppia.src.llms import HuggingFaceService

service = HuggingFaceService(
    api_key="hf_...",  # Your HuggingFace API key
    model="meta-llama/Llama-2-7b-chat-hf"  # Model name
)
```

### 6. Ollama (Local)
```python
from autoppia.src.llms import OllamaService

service = OllamaService(
    model="llama2",  # Model name
    base_url="http://localhost:11434"  # Ollama server URL
)
```

### 7. Local Models
```python
from autoppia.src.llms import LocalLLMService

# Llama model
llama_service = LocalLLMService(
    model_path="/path/to/llama-2-7b.gguf",
    model_type="llama"
)
```

## 🔄 Using Multiple Providers

```python
from autoppia.src.workers import WorkerConfig

config = WorkerConfig(
    name="multi-llm-worker",
    llms={
        "openai": OpenAIService(api_key="sk-...", model="gpt-4o"),
        "gemini": GoogleGeminiService(api_key="AIza...", model="gemini-pro"),
        "anthropic": AnthropicService(api_key="sk-ant-...", model="claude-3-opus")
    }
)

# Worker can switch between providers
worker = MultiLLMWorker(config)
worker.start()
worker.switch_provider("gemini")  # Switch to Gemini
response = worker.call("Hello!")
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

## 🧪 Testing Providers

```python
def check_provider_health(service):
    """Check if an LLM provider is working."""
    try:
        llm = service.get_llm()
        response = llm.predict("Hello")
        return True, response
    except Exception as e:
        return False, str(e)

# Test all providers
for name, service in providers.items():
    is_healthy, response = check_provider_health(service)
    print(f"{name}: {'✅' if is_healthy else '❌'} - {response}")
```

## 📚 Examples

See `autoppia/examples/multi_llm_worker.py` for a complete working example.
