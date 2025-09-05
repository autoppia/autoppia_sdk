"""
AI Workers for Autoppia SDK

This package provides the core worker system for creating, managing, and deploying
autonomous AI agents with support for various integrations and deployment options.

Quick Start:
    from autoppia.src.workers import AIWorker, WorkerConfig, WorkerAPI, run_worker_server
    
    # Simple way - use utility functions
    await run_worker_server(
        worker_id=123,
        worker_class=MyWorker,
        host="0.0.0.0",
        port=8081,
        worker_name="My Worker"
    )
    
    # Manual way - create configuration and start API
    config = get_worker_config(worker_id=123)
    worker = MyWorker(config)
    worker_api = await create_and_start_worker_api(123, MyWorker)
"""

from .interface import AIWorker, WorkerConfig
from .worker_api import WorkerAPI
from .router import WorkerRouter
from .adapter import AIWorkerConfigAdapter
from .worker_user_conf_service import WorkerUserConfService
from .worker_utils import get_worker_config, create_and_start_worker_api, run_worker_server

__all__ = [
    "AIWorker",
    "WorkerConfig",
    "WorkerAPI", 
    "WorkerRouter",
    "AIWorkerConfigAdapter",
    "WorkerUserConfService",
    "get_worker_config",
    "create_and_start_worker_api",
    "run_worker_server",
]
