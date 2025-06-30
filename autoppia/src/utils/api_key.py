"""
API Key verification utilities for Autoppia SDK.
"""
import os
import json
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
        
        # Make a direct POST request using the API client
        response = api_keys_api.api_client.call_api(
            '/api-keys/verify', 'POST',
            path_params={},
            query_params=[],
            header_params={'Content-Type': 'application/json'},
            body={'credential': api_key},
            response_type=None,
            auth_settings=['Basic'],
            _return_http_data_only=False,
            _preload_content=False
        )
        
        try:
            if response.status == 200:
                response_data = json.loads(response.data.decode('utf-8'))
                return response_data
            elif response.status == 401:
                return {"is_valid": False, "message": "Invalid API key"}
            else:
                # Create a requests.Response-like object for raise_for_status
                error_response = requests.Response()
                error_response.status_code = response.status
                error_response.raw = response
                error_response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if getattr(e.response, 'status_code', None) == 401:
                return {"is_valid": False, "message": "Invalid API key"}
            raise
