from typing import Dict, Type
from autoppia.src.llms.interface import LLMServiceInterface

class LLMRegistry:
    """Singleton registry for managing LLM services.
    
    This class provides a central registry for LLM services, allowing
    registration, initialization, and access to different LLM implementations.
    
    Attributes:
        _instance: Singleton instance
        _current_service (LLMServiceInterface): Currently active LLM service
        _services (Dict[str, Type[LLMServiceInterface]]): Registered service classes
    """

    _instance = None
    _current_service: LLMServiceInterface = None
    _services: Dict[str, Type[LLMServiceInterface]] = {}

    def __new__(cls):
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super(LLMRegistry, cls).__new__(cls)
        return cls._instance

    @classmethod
    def register_service(cls, name: str, service_class: Type[LLMServiceInterface]) -> None:
        """Register a new LLM service.
        
        Args:
            name (str): Name to register the service under
            service_class (Type[LLMServiceInterface]): Service class to register
        """
        cls._services[name] = service_class

    @classmethod
    def get_service(cls) -> LLMServiceInterface:
        """Get the current LLM service.
        
        Returns:
            LLMServiceInterface: Currently initialized service
            
        Raises:
            RuntimeError: If no service has been initialized
        """
        if not cls._current_service:
            raise RuntimeError("No LLM service has been initialized")
        return cls._current_service

    @classmethod
    def initialize_service(cls, name: str, **kwargs) -> None:
        """Initialize a specific LLM service.
        
        Args:
            name (str): Name of the service to initialize
            **kwargs: Arguments to pass to the service constructor
            
        Raises:
            ValueError: If the service name is not registered
        """
        if name not in cls._services:
            raise ValueError(f"Unknown LLM service: {name}")
        
        service_class = cls._services[name]
        cls._current_service = service_class(**kwargs)

    @classmethod
    def available_services(cls) -> list[str]:
        """Get list of available service names.
        
        Returns:
            list[str]: Names of all registered services
        """
        return list(cls._services.keys()) 