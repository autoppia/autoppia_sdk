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
        payload: Optional[dict] = None,
    ):
        """Make an HTTP request to a specified API endpoint.

        Auth strategy:
            - If api_key is provided, use it as Bearer token.
            - Else if auth_url, username, and password are provided, obtain access token via POST and use it.

        Args:
            url: The endpoint path to be appended to the domain URL
            method: HTTP method to use (get, post, put, patch, delete)
            payload: Data to be sent in the request body (required for non-GET requests)

        Returns:
            dict or str or None: JSON response for GET requests, "Success!" for other successful
            requests, None if an error occurs, or error message string for invalid inputs
        """
        full_url = f"{self.domain_url}{url}"

        # Resolve Authorization header
        token = None
        if self.api_key:
            token = self.api_key
        elif self.auth_url and self.username and self.password:
            try:
                auth_body = {"email": self.username, "password": self.password}
                auth_resp = requests.post(self.auth_url, json=auth_body)
                auth_resp.raise_for_status()
                token = auth_resp.json().get("access")
            except requests.HTTPError as http_err:
                print(f"HTTP error occurred during authentication: {http_err}")
                return None
            except Exception as err:
                print(f"An error occurred during authentication: {err}")
                return None

        headers = {"Authorization": f"Bearer {token}"} if token else {}

        method = method.lower()
        valid_methods = {"get", "post", "put", "patch", "delete"}
        if method not in valid_methods:
            return "Invalid method provided"

        request_func = getattr(requests, method)

        try:
            if method == "get":
                response = request_func(full_url, headers=headers)
            else:
                if payload is None:
                    return "Payload is required for this method"
                response = request_func(full_url, headers=headers, json=payload)

            response.raise_for_status()
            return response.json() if method == "get" else "Success!"
        except requests.HTTPError as http_err:
            print(f"HTTP error occurred while calling endpoint: {http_err}")
            return None
        except Exception as err:
            print(f"An error occurred while calling endpoint: {err}")
            return None

    