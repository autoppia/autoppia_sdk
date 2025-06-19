"""
API Key verification utilities for Autoppia SDK.
"""
import os
from typing import Optional, Dict, Union
import requests
from urllib.parse import urljoin
from autoppia_backend_client.api_client import ApiClient
from autoppia_backend_client.configuration import Configuration
from autoppia_backend_client.api.api_keys_api import ApiKeysApi
from autoppia_backend_client.models import ApiKey as ApiKeyDTO

class ApiKeyVerifier:
    """Utility class for verifying Autoppia API keys."""

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the API key verifier.

        Args:
            base_url (Optional[str]): Base URL for the Autoppia API. 
                     If not provided, will try to get from AUTOPPIA_API_URL environment variable.
        """

        config = Configuration()
        config.host = base_url or os.getenv("AUTOPPIA_API_URL", "https://api.autoppia.com")
        self.api_client = ApiClient(configuration=config)


    def verify_api_key(self, api_key: str) -> Dict[str, Union[bool, str]]:
        """
        Verify an Autoppia API key.

        Args:
            api_key (str): The API key to verify.

        Returns:
            Dict[str, Union[bool, str]]: Response containing verification status and details.
                {
                    'is_valid': bool,
                    'message': str,
                    'name': str (only if valid)
                }

        Raises:
            requests.exceptions.RequestException: If there's an error communicating with the API
            ValueError: If the API key is empty or invalid format
        """
        api_keys_api = ApiKeysApi(self.api_client)
        data = {
            "credential": api_key
        }

        response = api_keys_api.api_keys_verify(data)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            return {"is_valid": False, "message": "Invalid API key"}
        else:
            response.raise_for_status()
