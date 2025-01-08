from abc import ABC, abstractmethod
from typing import Any, Dict

class LLMService(ABC):
    """Base interface for LLM services that can be used by agents"""
    
    @abstractmethod
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the LLM service with specific settings"""
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate text using the LLM""" 