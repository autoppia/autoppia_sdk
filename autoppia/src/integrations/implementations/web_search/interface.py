from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class WebSearchIntegration(ABC):
    """Abstract base class for web search integration implementations.
    
    This class defines the interface for integrating with various web search engines
    and APIs. Concrete implementations should inherit from this class and implement
    the required methods.
    """

    @abstractmethod
    def call_endpoint(
        self,
        query: str,
        num_results: int = 5
    ):
        """Makes a call to the web search endpoint with the specified query.
        
        Args:
            query (str): The search query or request to send to the endpoint.
            num_results (int, optional): Maximum number of results to return. Defaults to 5.
            
        Returns:
            Response from the endpoint (implementation-specific return type).
            
        Raises:
            NotImplementedError: If the concrete class doesn't implement this method.
        """
        pass
