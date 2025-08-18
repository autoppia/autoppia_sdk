"""
Autoppia SDK - Autonomous AI Workers Platform

A comprehensive SDK for creating, deploying, and managing autonomous AI agents
with support for multiple LLM providers, integrations, and deployment options.

Quick Start:
    from autoppia import AutomataAgent, AutomataClient
    from autoppia.workers import AIWorker, WorkerConfig
    from autoppia.llms import LLMRegistry, LLMProviderConfig, create_openai_provider
    
    # Create an agent
    agent = AutomataAgent(api_key="your-api-key")
    
    # Run a task
    result = await agent.run_locally("Navigate to website and extract data")
    
    # Create a worker
    worker = AIWorker()
    worker.start()
"""

# Core automata functionality
from .automata.agent import AutomataAgent
from .automata.client import AutomataClient

# Worker system
from .src.workers.interface import AIWorker, WorkerConfig
from .src.workers.worker_api import WorkerAPI
from .src.workers.router import WorkerRouter

# LLM services (framework-agnostic)
from .src.llms.registry import LLMRegistry
from .src.llms.interface import LLMServiceInterface
from .src.llms.providers import SimpleLLMProvider

# Integration system
from .src.integrations.interface import IntegrationInterface
from .src.integrations.adapter import IntegrationsAdapter

# Utilities and adapters
from .src.workers.adapter import AIWorkerConfigAdapter

# Version info
__version__ = "0.1.0"
__author__ = "Autoppia Team"
__email__ = "support@autoppia.com"

# Public API
__all__ = [
    # Core classes
    "AutomataAgent",
    "AutomataClient",
    
    # Worker system
    "AIWorker",
    "WorkerConfig",
    "WorkerAPI",
    "WorkerRouter",
    
    # LLM services (framework-agnostic)
    "LLMRegistry",
    "LLMServiceInterface",
    "SimpleLLMProvider",
    
    # Integration system
    "IntegrationInterface",
    "IntegrationsAdapter",
    
    # Utilities
    "AIWorkerConfigAdapter",
]
