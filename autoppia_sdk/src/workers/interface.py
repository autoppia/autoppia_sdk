from abc import ABC, abstractmethod
from autoppia_sdk.src.integrations.interface import IntegrationInterface
from autoppia_sdk.src.llms.interface import LLMServiceInterface
from autoppia_sdk.src.vectorstores.interface import VectorStoreInterface
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class WorkerConfig:
    name: str = None
    system_prompt: str = None
    integrations: Dict = field(default_factory=dict)
    llms: Dict = field(default_factory=dict)
    vectorstores: Dict = field(default_factory=dict)
    extra_arguments: Dict = field(default_factory=dict)


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
