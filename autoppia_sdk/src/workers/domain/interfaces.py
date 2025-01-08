from abc import ABC, abstractmethod
from typing import Any, Dict

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
