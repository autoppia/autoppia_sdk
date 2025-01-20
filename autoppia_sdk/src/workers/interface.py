from abc import ABC, abstractmethod
from autoppia_sdk.src.integrations.interface import IntegrationInterface
from autoppia_sdk.src.llms.interface import LLMServiceInterface
from autoppia_sdk.src.vectorstores.interface import VectorStoreInterface


class WorkerConfig():
    instructions: str
    system_prompt: str
    integrations: dict[IntegrationInterface]
    llms: dict[str, LLMServiceInterface]
    vectorstores: dict[str, VectorStoreInterface]
    extra_arguments: dict[str, str]


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
