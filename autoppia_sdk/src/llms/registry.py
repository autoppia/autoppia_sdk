from typing import Dict, Type
from autoppia_sdk.src.llms.interface import LLMServiceInterface

class LLMRegistry:
    _instance = None
    _current_service: LLMServiceInterface = None
    _services: Dict[str, Type[LLMServiceInterface]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMRegistry, cls).__new__(cls)
        return cls._instance

    @classmethod
    def register_service(cls, name: str, service_class: Type[LLMServiceInterface]) -> None:
        """Register a new LLM service"""
        cls._services[name] = service_class

    @classmethod
    def get_service(cls) -> LLMServiceInterface:
        """Get the current LLM service"""
        if not cls._current_service:
            raise RuntimeError("No LLM service has been initialized")
        return cls._current_service

    @classmethod
    def initialize_service(cls, name: str, **kwargs) -> None:
        """Initialize a specific LLM service"""
        if name not in cls._services:
            raise ValueError(f"Unknown LLM service: {name}")
        
        service_class = cls._services[name]
        cls._current_service = service_class(**kwargs)

    @classmethod
    def available_services(cls) -> list[str]:
        """Get list of available service names"""
        return list(cls._services.keys()) 