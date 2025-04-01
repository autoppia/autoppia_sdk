from abc import ABC, abstractmethod
from autoppia_sdk.src.workers.interface import AIWorker, WorkerConfig
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class AppConfig(WorkerConfig):
    """Configuration container for app instances.
    
    Extends WorkerConfig to include app-specific configuration parameters.
    
    Attributes:
        workers: Dictionary of worker instances keyed by worker name
        app_type: Type of the application (e.g., chatbot, assistant, etc.)
        ui_config: Configuration for the app's user interface
        permissions: List of permissions required by the app
        metadata: Additional metadata for the app
    """
    
    workers: Dict[str, AIWorker] = field(default_factory=dict)
    app_type: Optional[str] = None
    ui_config: Dict[str, Any] = field(default_factory=dict)
    permissions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AIApp(AIWorker, ABC):
    """Base interface that all AI applications must implement.
    
    This abstract class extends the AIWorker interface to provide additional
    functionality required for full AI applications. While workers represent
    individual AI agents, apps represent complete applications that may
    coordinate multiple workers and provide additional features.
    """

    @abstractmethod
    def register_worker(self, worker_name: str, worker: AIWorker) -> None:
        """Register a worker with the application.
        
        Args:
            worker_name: Unique identifier for the worker
            worker: The worker instance to register
            
        This method allows the application to incorporate multiple workers
        and coordinate their activities.
        """
    
    @abstractmethod
    def get_worker(self, worker_name: str) -> AIWorker:
        """Retrieve a registered worker by name.
        
        Args:
            worker_name: The name of the worker to retrieve
            
        Returns:
            AIWorker: The requested worker instance
            
        Raises:
            KeyError: If the worker is not registered
        """
    
    @abstractmethod
    def get_workers(self) -> Dict[str, AIWorker]:
        """Retrieve all registered workers.
        
        Returns:
            Dict[str, AIWorker]: Dictionary of all registered workers
        """
    
    @abstractmethod
    def route_message(self, message: str, worker_name: Optional[str] = None) -> str:
        """Route a message to a specific worker or determine the appropriate worker.
        
        Args:
            message: The input message to be processed
            worker_name: Optional name of the worker to route the message to
            
        Returns:
            str: The response from the worker
            
        If worker_name is provided, the message is routed to that specific worker.
        Otherwise, the application determines the appropriate worker based on the
        message content and routing rules.
        """
    
    @abstractmethod
    def get_ui_config(self) -> Dict[str, Any]:
        """Retrieve the UI configuration for the application.
        
        Returns:
            Dict[str, Any]: The UI configuration
            
        This method provides configuration information for rendering the
        application's user interface.
        """
    
    @abstractmethod
    def get_app_info(self) -> Dict[str, Any]:
        """Retrieve information about the application.
        
        Returns:
            Dict[str, Any]: Information about the application
            
        This method provides metadata and other information about the
        application, such as its name, description, version, etc.
        """
