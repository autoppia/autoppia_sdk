from typing import Dict, Optional, Any, Callable
import logging
from autoppia.src.apps.interface import AIApp, AppConfig
from autoppia.src.workers.interface import AIWorker

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BaseApp")


class BaseAIApp(AIApp):
    """Base implementation of the AIApp interface.
    
    This class provides a starting point for implementing AI applications by
    providing default implementations of the AIApp interface methods.
    
    Attributes:
        config: The configuration for the app
        workers: Dictionary of worker instances keyed by worker name
    """
    
    def __init__(self, config: AppConfig):
        """Initialize the BaseAIApp.
        
        Args:
            config: The configuration for the app
        """
        self.config = config
        self.workers: Dict[str, AIWorker] = {}
        self._initialized = False
    
    def start(self) -> None:
        """Initialize the app and any required resources."""
        if self._initialized:
            logger.warning("App already initialized")
            return
        
        logger.info(f"Starting app: {self.config.name}")
        
        # Initialize workers
        for worker_name, worker in self.workers.items():
            try:
                logger.info(f"Starting worker: {worker_name}")
                worker.start()
            except Exception as e:
                logger.error(f"Error starting worker {worker_name}: {e}")
                raise RuntimeError(f"Failed to start worker {worker_name}: {str(e)}")
        
        self._initialized = True
        logger.info(f"App {self.config.name} started successfully")
    
    def stop(self) -> None:
        """Cleanup and release any resources."""
        if not self._initialized:
            logger.warning("App not initialized")
            return
        
        logger.info(f"Stopping app: {self.config.name}")
        
        # Stop workers
        for worker_name, worker in self.workers.items():
            try:
                logger.info(f"Stopping worker: {worker_name}")
                worker.stop()
            except Exception as e:
                logger.error(f"Error stopping worker {worker_name}: {e}")
        
        self._initialized = False
        logger.info(f"App {self.config.name} stopped successfully")
    
    def call(self, message: str) -> str:
        """Process a message and return a response.
        
        This implementation routes the message to the appropriate worker based on
        content analysis or uses a default worker if available.
        
        Args:
            message: The input message to be processed
            
        Returns:
            str: The response from the worker
        """
        return self.route_message(message)
    
    def call_stream(self, message: str, callback: Callable[[Any], None], worker_name: Optional[str] = None) -> Optional[str]:
        """Process a message with streaming and return a final response.
        
        This implementation routes the message to the appropriate worker based on
        content analysis or uses a default worker if available, with streaming support.
        
        Args:
            message: The input message to be processed
            callback: Function to call with streaming chunks
            worker_name: Optional name of the worker to route the message to
            
        Returns:
            Optional[str]: The final response from the worker, if any
        """
        if not self._initialized:
            raise RuntimeError("App not initialized")
        
        if not self.workers:
            raise ValueError("No workers registered")
        
        # If worker_name is provided, route to that worker
        if worker_name:
            if worker_name not in self.workers:
                raise ValueError(f"Worker {worker_name} not found")
            
            worker = self.workers[worker_name]
            
            # Check if the worker supports streaming
            if hasattr(worker, 'call_stream'):
                return worker.call_stream(message, callback)
            else:
                # Fallback to non-streaming call
                result = worker.call(message)
                callback(result)
                return result
        
        # If no worker_name is provided, use a simple routing strategy
        # In a real implementation, this would use more sophisticated routing
        
        # For now, just use the first worker
        default_worker_name = next(iter(self.workers))
        default_worker = self.workers[default_worker_name]
        
        # Check if the worker supports streaming
        if hasattr(default_worker, 'call_stream'):
            return default_worker.call_stream(message, callback)
        else:
            # Fallback to non-streaming call
            result = default_worker.call(message)
            callback(result)
            return result
    
    def register_worker(self, worker_name: str, worker: AIWorker) -> None:
        """Register a worker with the application.
        
        Args:
            worker_name: Unique identifier for the worker
            worker: The worker instance to register
        """
        if worker_name in self.workers:
            logger.warning(f"Worker {worker_name} already registered, replacing")
        
        self.workers[worker_name] = worker
        logger.info(f"Registered worker: {worker_name}")
    
    def get_worker(self, worker_name: str) -> AIWorker:
        """Retrieve a registered worker by name.
        
        Args:
            worker_name: The name of the worker to retrieve
            
        Returns:
            AIWorker: The requested worker instance
            
        Raises:
            KeyError: If the worker is not registered
        """
        if worker_name not in self.workers:
            raise KeyError(f"Worker {worker_name} not found")
        
        return self.workers[worker_name]
    
    def get_workers(self) -> Dict[str, AIWorker]:
        """Retrieve all registered workers.
        
        Returns:
            Dict[str, AIWorker]: Dictionary of all registered workers
        """
        return self.workers
    
    def route_message(self, message: str, worker_name: Optional[str] = None) -> str:
        """Route a message to a specific worker or determine the appropriate worker.
        
        Args:
            message: The input message to be processed
            worker_name: Optional name of the worker to route the message to
            
        Returns:
            str: The response from the worker
            
        Raises:
            ValueError: If no workers are registered or the specified worker is not found
            RuntimeError: If the app is not initialized
        """
        if not self._initialized:
            raise RuntimeError("App not initialized")
        
        if not self.workers:
            raise ValueError("No workers registered")
        
        # If worker_name is provided, route to that worker
        if worker_name:
            if worker_name not in self.workers:
                raise ValueError(f"Worker {worker_name} not found")
            
            return self.workers[worker_name].call(message)
        
        # If no worker_name is provided, use a simple routing strategy
        # In a real implementation, this would use more sophisticated routing
        
        # For now, just use the first worker
        default_worker_name = next(iter(self.workers))
        return self.workers[default_worker_name].call(message)
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Retrieve the UI configuration for the application.
        
        Returns:
            Dict[str, Any]: The UI configuration
        """
        return self.config.ui_config
    
    def get_app_info(self) -> Dict[str, Any]:
        """Retrieve information about the application.
        
        Returns:
            Dict[str, Any]: Information about the application
        """
        return {
            "name": self.config.name,
            "app_type": self.config.app_type,
            "workers": list(self.workers.keys()),
            "metadata": self.config.metadata
        }
