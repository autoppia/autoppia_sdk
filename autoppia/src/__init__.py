"""
Autoppia SDK Core Components

This package contains the core implementation components for the Autoppia SDK:
- Workers: AI agent implementations and management
- LLMs: Language model service integrations
- Integrations: External service connectors
- Vectorstores: Vector database integrations
- Toolkits: Pre-built tool collections
- Utils: Common utilities and helpers
"""

# Core components
from .workers.interface import AIWorker, WorkerConfig
from .workers.worker_api import WorkerAPI
from .workers.router import WorkerRouter
from .workers.adapter import AIWorkerConfigAdapter

from .llms.interface import LLMServiceInterface
from .llms.providers import OpenAIService, AnthropicService
from .llms.registry import LLMRegistry
from .llms.adapter import LLMAdapter

from .integrations.interface import IntegrationInterface
from .integrations.adapter import IntegrationsAdapter
from .integrations.config import IntegrationConfig

# Public API for src package
__all__ = [
    # Workers
    "AIWorker",
    "WorkerConfig", 
    "WorkerAPI",
    "WorkerRouter",
    "AIWorkerConfigAdapter",
    
    # LLMs
    "LLMServiceInterface",
    "OpenAIService",
    "AnthropicService",
    "LLMRegistry",
    "LLMAdapter",
    
    # Integrations
    "IntegrationInterface",
    "IntegrationsAdapter",
    "IntegrationConfig",
]
