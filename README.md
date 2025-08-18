# 🧠 Autoppia SDK

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/autoppia-sdk.svg)](https://badge.fury.io/py/autoppia-sdk)

**Autoppia SDK** is a comprehensive Python SDK for creating, deploying, and managing autonomous AI agents. Built with enterprise-grade architecture, it provides seamless integration with multiple LLM providers, external services, and deployment platforms.

## 🚀 Features

- **🤖 Autonomous AI Workers**: Create intelligent agents that can process tasks independently
- **🔌 Multi-Provider LLM Support**: OpenAI, Anthropic, Google Gemini, Cohere, HuggingFace, Ollama, and local models
- **🌐 Web Automation**: Built-in browser automation with the Automata client
- **🔗 Rich Integrations**: Web search, email, database, and API integrations
- **📊 Vector Database Support**: Built-in vector storage for knowledge management
- **⚡ Async-First Design**: High-performance asynchronous operations
- **🛡️ Enterprise Security**: Comprehensive error handling and validation
- **📦 Easy Deployment**: Simple deployment and scaling of AI workers

## 📦 Installation

```bash
pip install autoppia-sdk
```

Or install from source:

```bash
git clone https://github.com/autoppia/autoppia-sdk.git
cd autoppia-sdk
pip install -e .
```

## 🎯 Quick Start

### 1. Basic Usage

```python
from autoppia import AutomataAgent, AutomataClient

# Initialize the agent
agent = AutomataAgent(api_key="your-api-key")

# Run a web automation task
result = await agent.run_locally(
    task="Navigate to example.com and extract the main heading",
    initial_url="https://example.com"
)

print(f"Task completed: {result}")
```

### 2. Create a Custom AI Worker

```python
from autoppia.src.workers import AIWorker, WorkerConfig
from autoppia.src.llms import OpenAIService

# Define worker configuration
config = WorkerConfig(
    name="my-assistant",
    system_prompt="You are a helpful AI assistant.",
    llms={
        "openai": OpenAIService(
            api_key="your-openai-key",
            model="gpt-4o"
        )
    }
)

# Create and use the worker
class MyWorker(AIWorker):
    def __init__(self, config):
        self.config = config
    
    def start(self):
        # Initialize resources
        pass
    
    def call(self, message: str) -> str:
        # Process message and return response
        return "Hello! I'm your AI assistant."
    
    def stop(self):
        # Cleanup resources
        pass

worker = MyWorker(config)
worker.start()
response = worker.call("Hello!")
worker.stop()
```

### 3. Use Multiple LLM Services

```python
from autoppia.src.llms import LLMRegistry, OpenAIService, GoogleGeminiService

# Register multiple LLM services
LLMRegistry.register_service("openai", OpenAIService)
LLMRegistry.register_service("gemini", GoogleGeminiService)

# Initialize services
LLMRegistry.initialize_service("openai", api_key="your-openai-key", model="gpt-4")
LLMRegistry.initialize_service("gemini", api_key="your-google-key", model="gemini-pro")

# Get and use different services
openai_llm = LLMRegistry.get_service("openai").get_llm()
gemini_llm = LLMRegistry.get_service("gemini").get_llm()

# Compare responses
openai_response = openai_llm.predict("What is the capital of France?")
gemini_response = gemini_llm.predict("What is the capital of France?")

print(f"OpenAI: {openai_response}")
print(f"Gemini: {gemini_response}")
```

## 🏗️ Architecture

The Autoppia SDK is built with a modular, extensible architecture:

```
autoppia/
├── automata/           # Web automation client
├── src/
│   ├── workers/       # AI worker system
│   ├── llms/          # Language model services
│   ├── integrations/  # External service connectors
│   ├── vectorstores/  # Vector database support
│   ├── toolkits/      # Pre-built tool collections
│   ├── utils/         # Common utilities
│   └── config.py      # Configuration management
└── examples/          # Usage examples
```

## 🔧 Configuration

### Environment Variables

```bash
export AUTOPPIA_API_KEY="your-api-key"
export AUTOPPIA_BASE_URL="https://api.autoppia.com/api/v1"
export AUTOPPIA_LOG_LEVEL="INFO"
export AUTOPPIA_DEBUG="false"
```

### Configuration File

```python
from autoppia.src.config import SDKConfig

# Load configuration
config = SDKConfig.load_from_file("config.json")

# Or create custom configuration
config = SDKConfig(
    api_key="your-key",
    log_level="DEBUG",
    default_llm_provider="openai"
)

# Save configuration
config.save_to_file("my-config.json")
```

## 📚 Examples

### Web Automation

```python
from autoppia import AutomataAgent

async def automate_website():
    agent = AutomataAgent(api_key="your-key")
    
    try:
        result = await agent.run_locally(
            task="Fill out the contact form on example.com",
            initial_url="https://example.com/contact",
            max_steps=100
        )
        print(f"Automation completed: {result}")
    finally:
        await agent.close()

# Run the automation
await automate_website()
```

### Custom Integration

```python
from autoppia.src.integrations import IntegrationInterface

class WeatherIntegration(IntegrationInterface):
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def get_weather(self, city: str):
        # Implementation for weather API
        pass

# Use in worker configuration
config = WorkerConfig(
    name="weather-bot",
    integrations={
        "weather": WeatherIntegration(api_key="weather-api-key")
    }
)
```

### Vector Database Integration

```python
from autoppia.src.vectorstores import VectorStoreInterface

class CustomVectorStore(VectorStoreInterface):
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
    
    async def store_embedding(self, text: str, embedding: list):
        # Store embedding implementation
        pass
    
    async def search_similar(self, embedding: list, limit: int = 5):
        # Search implementation
        pass
```

## 🚀 Deployment

### Local Development

```python
from autoppia.src.workers import WorkerAPI

# Start worker API server
api = WorkerAPI(host="localhost", port=8000)
await api.start()
```

### Production Deployment

```python
from autoppia.src.workers import WorkerRouter

# Create worker router for load balancing
router = WorkerRouter()
router.add_worker("worker-1", "localhost:8001")
router.add_worker("worker-2", "localhost:8002")

# Start routing
await router.start()
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=autoppia

# Run specific test file
pytest tests/test_workers.py
```

## 📖 API Reference

### Core Classes

- **`AutomataAgent`**: Web automation agent
- **`AIWorker`**: Base class for AI workers
- **`WorkerConfig`**: Worker configuration container
- **`LLMRegistry`**: Language model service registry
- **`IntegrationInterface`**: Base class for integrations

### Key Methods

- **`worker.start()`**: Initialize worker resources
- **`worker.call(message)`**: Process incoming message
- **`worker.stop()`**: Cleanup worker resources
- **`llm.predict(prompt)`**: Generate LLM response

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.autoppia.com](https://docs.autoppia.com)
- **Issues**: [GitHub Issues](https://github.com/autoppia/autoppia-sdk/issues)
- **Discussions**: [GitHub Discussions](https://github.com/autoppia/autoppia-sdk/discussions)
- **Email**: support@autoppia.com

## 🔗 Links

- **Website**: [autoppia.com](https://autoppia.com)
- **API Documentation**: [api.autoppia.com](https://api.autoppia.com)
- **Community**: [community.autoppia.com](https://community.autoppia.com)

---

**Made with ❤️ by the Autoppia Team**
