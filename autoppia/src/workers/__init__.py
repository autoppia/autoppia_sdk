"""
AI Workers for Autoppia SDK

This package provides the core worker system for creating, managing, and deploying
autonomous AI agents with support for various integrations and deployment options.

Quick Start:
    from autoppia.src.workers import AIWorker, WorkerConfig, WorkerAPI
    
    # Create a worker configuration
    config = WorkerConfig(
        name="my-worker",
        system_prompt="You are a helpful AI assistant",
        llms={"openai": openai_service}
    )
    
    # Start the worker
    worker = MyWorker(config)
    worker.start()
"""

from .interface import AIWorker, WorkerConfig
from .worker_api import WorkerAPI
from .router import WorkerRouter
from .adapter import AIWorkerConfigAdapter
from .worker_user_conf_service import WorkerUserConfService

__all__ = [
    "AIWorker",
    "WorkerConfig",
    "WorkerAPI", 
    "WorkerRouter",
    "AIWorkerConfigAdapter",
    "WorkerUserConfService",
]
