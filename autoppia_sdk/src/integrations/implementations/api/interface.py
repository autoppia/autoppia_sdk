from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class APIIntegration(ABC):
    """Abstract base class for API integration implementations.

    This class defines the interface for making API calls to external services.
    All concrete API integration implementations should inherit from this class
    and implement the required methods.
    """

    @abstractmethod
    def call_endpoint(
        self,
        url: str,
        method: str,
        payload: dict
    ):
        """Makes an HTTP request to the specified API endpoint.

        Args:
            url (str): The complete URL of the API endpoint to call.
            method (str): The HTTP method to use (e.g., 'GET', 'POST', 'PUT', 'DELETE').
            payload (dict): The request payload/body to send with the request.

        Returns:
            The response from the API endpoint. The specific return type should be
            defined by the implementing class.

        Raises:
            Should define specific exceptions that may be raised in implementations.
        """
        pass
