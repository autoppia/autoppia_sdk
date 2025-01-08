from abc import ABC, abstractmethod
from typing import Any, Dict, List

class VectorStore(ABC):
    """Base interface for vector stores that can be used by agents"""
    
    @abstractmethod
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the vector store with specific settings"""
    
    @abstractmethod
    def search(self, query: str, **kwargs) -> List[Any]:
        """Search for similar vectors""" 