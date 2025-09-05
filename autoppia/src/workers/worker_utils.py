"""
Worker utility functions for easy worker configuration and startup.

This module provides convenient functions for initializing and starting workers
with configuration from the Autoppia backend.
"""

import os
import asyncio
from typing import Optional
from .worker_user_conf_service import WorkerUserConfService
from .worker_api import WorkerAPI
from .adapter import AIWorkerConfigAdapter
from .interface import WorkerConfig


def get_worker_config(worker_id: int) -> WorkerConfig:
    """
    Initialize a worker configuration from the Autoppia backend.
    
    Args:
        worker_id (int): The ID of the worker to configure
        
    Returns:
        WorkerConfig: The configured worker configuration
        
    Raises:
        RuntimeError: If worker_id is not provided or configuration fails
    """
    print("Loading worker configuration...")
    
    if not worker_id:
        raise RuntimeError("worker_id parameter is required")

    print(f"Worker ID: {worker_id}")

    # Get Worker Config DTO from autoppia backend
    worker_service = WorkerUserConfService()
    worker_config_dto = worker_service.retrieve_worker_config(worker_id=worker_id)

    # Adapt this DTO into a WorkerConfig class we do understand
    worker_config_adapter = AIWorkerConfigAdapter(worker_id)
    worker_config: WorkerConfig = worker_config_adapter.from_autoppia_user_backend(worker_config_dto)
    
    print(f"Worker configuration loaded: {worker_config.name}")
    return worker_config


async def create_and_start_worker_api(
    worker_id: int,
    worker_class,
    host: str = "0.0.0.0",
    port: int = 8081,
    worker_name: str = "Worker"
) -> WorkerAPI:
    """
    Create and start a WebSocket worker API.
    
    Args:
        worker_id (int): The ID of the worker to configure
        worker_class: The worker class to instantiate
        host (str): Host to bind the server to (default: "0.0.0.0")
        port (int): Port to bind the server to (default: 8081)
        worker_name (str): Name for display purposes (default: "Worker")
    
    Returns:
        WorkerAPI: The started worker API instance
    """
    print(f"=== {worker_name} WebSocket Server ===")
    print(f"Initializing {worker_name} with WebSocket support...")
    
    # Initialize your worker with the worker config
    worker_config = get_worker_config(worker_id)
    worker = worker_class(worker_config)
    
    # Create the WorkerAPI instance with WebSocket support
    worker_api = WorkerAPI(
        worker=worker,
        host=host,
        port=port
    )
    
    print(f"Starting WebSocket server on ws://{host}:{port}")
    print("Features enabled:")
    print("  ✅ WebSocket communication")
    print("  ✅ Streaming AI responses") 
    print("  ✅ Worker processing capabilities")
    print("  ✅ OpenAI Assistant integration")
    print("  ✅ Vector store support")
    print()
    print("You can connect to this worker using:")
    print(f"  - WebSocket client: ws://localhost:{port}")
    print(f"  - Python router: WorkerRouter('localhost', {port})")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the server (this will run indefinitely)
    await worker_api.start()
    
    return worker_api


async def run_worker_server(
    worker_id: int,
    worker_class,
    host: str = "0.0.0.0",
    port: int = 8081,
    worker_name: str = "Worker"
) -> None:
    """
    Run a worker server with proper error handling and cleanup.
    
    Args:
        worker_id (int): The ID of the worker to configure
        worker_class: The worker class to instantiate
        host (str): Host to bind the server to (default: "0.0.0.0")
        port (int): Port to bind the server to (default: 8081)
        worker_name (str): Name for display purposes (default: "Worker")
    """
    worker_api = None
    try:
        # Create and start the worker API
        worker_api = await create_and_start_worker_api(
            worker_id=worker_id,
            worker_class=worker_class,
            host=host,
            port=port,
            worker_name=worker_name
        )
        
    except KeyboardInterrupt:
        print(f"\nShutting down {worker_name}...")
        if worker_api:
            await worker_api.stop()
        print(f"{worker_name} stopped successfully")
        
    except Exception as e:
        print(f"Error starting {worker_name}: {e}")
        raise
