from typing import Optional
from autoppia.src.integrations.implementations.api.interface import APIIntegration
from autoppia.src.integrations.config import IntegrationConfig
from autoppia.src.integrations.implementations.base import Integration
import requests


class AutoppiaIntegration(APIIntegration, Integration):
    """A class that handles API integration with Autoppia services.

    This integration class provides functionality to make API calls to Autoppia endpoints
    using various authentication methods including API keys, username/password, and bearer tokens.

    Attributes:
        integration_config (IntegrationConfig): Configuration object containing integration settings
        api_key (str): API key for authentication
        username (str): Username for authentication
        password (str): Password for authentication
        auth_url (str): URL for authentication endpoint
        domain_url (str): Base URL for API endpoints
    """

    def __init__(self, integration_config: IntegrationConfig):
        """Initialize the Autoppia Integration.

        Args:
            integration_config (IntegrationConfig): Configuration object containing
                necessary attributes for the integration
        """
        self.integration_config = integration_config
        self.api_key = integration_config.attributes.get("api_key")
        self.username = integration_config.attributes.get("username")
        self.password = integration_config.attributes.get("password")
        self.auth_url = integration_config.attributes.get("auth_url")
        self.domain_url = integration_config.attributes.get("domain_url")

    def call_endpoint(
        self,
        url: str,
        method: str,
        payload: dict
    ):
        """Make an HTTP request to a specified API endpoint.

        Args:
            url (str): The endpoint path to be appended to the domain URL
            method (str): HTTP method to use (get, post, put, patch, delete)
            payload (dict): Data to be sent in the request body (required for non-GET requests)

        Returns:
            dict or str or None: JSON response for GET requests, "Success!" for other successful
                requests, None if an error occurs, or error message string for invalid inputs

        Raises:
            requests.HTTPError: If the HTTP request fails
            Exception: For any other errors during the request
        """
        full_url = f"{self.domain_url}{url}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        method = method.lower()
        valid_methods = {"get", "post", "put", "patch", "delete"}

        if method not in valid_methods:
            return "Invalid method provided"
        
        request_func = getattr(requests, method)

        try:
            if method == "get":
                response = request_func(full_url, headers=headers)
            else:
                if not payload:
                    return "Payload is required for this method"

                response = request_func(full_url, headers=headers, json=payload)

            response.raise_for_status()

            result = response.json() if method == "get" else "Success!"

            return result

        except requests.HTTPError as http_err:
            print(f"HTTP error occurred while calling endpoint: {http_err}")
            return None
        except Exception as err:
            print(f"An error occurred while calling endpoint: {err}")
            return None

    