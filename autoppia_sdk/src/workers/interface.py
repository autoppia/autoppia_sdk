from abc import ABC, abstractmethod
from autoppia_sdk.src.integrations.interface import IntegrationInterface
from autoppia_sdk.src.llms.interface import LLMServiceInterface
from autoppia_sdk.src.vectorstores.interface import VectorStoreInterface
from dataclasses import dataclass, field
from typing import Dict, Optional, Any


@dataclass
class WorkerConfig:
    """Configuration container for worker instances.
    
    Attributes:
        name: Unique identifier for the worker configuration
        system_prompt: Base prompt template for the worker
        integrations: Dictionary of integration clients keyed by provider
        llms: Dictionary of LLM services keyed by provider
        vectorstores: Dictionary of vector stores keyed by provider
        extra_arguments: Additional provider-specific configuration parameters
    """
    
    name: str
    system_prompt: Optional[str] = None
    integrations: Dict[str, IntegrationInterface] = field(default_factory=dict)
    llms: Dict[str, LLMServiceInterface] = field(default_factory=dict)
    vectorstores: Dict[str, VectorStoreInterface] = field(default_factory=dict)
    extra_arguments: Dict[str, Any] = field(default_factory=dict)


class AIWorker(ABC):
    """Base interface that all marketplace agents must implement"""

    @abstractmethod
    def start(self) -> None:
        """Initialize the agent and any required resources"""

    @abstractmethod
    def stop(self) -> None:
        """Cleanup and release any resources"""

    @abstractmethod
    def call(self, message: str) -> str:
        """Process a message and return a response"""
