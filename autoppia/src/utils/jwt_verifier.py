"""
JWT verification utilities for Autoppia SDK.

Verifies browser-issued JWTs by calling the Autoppia backend verification endpoint.
Aligned in structure with ApiKeyVerifier for consistency.
"""

import os
from typing import Optional, Dict, Union
from autoppia_backend_client.api_client import ApiClient
from autoppia_backend_client.configuration import Configuration
import json
import requests


class JWTVerifier:
    """Utility class for verifying Autoppia JWT access tokens."""

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the JWT verifier.

        Args:
            base_url (Optional[str]): Base URL for the Autoppia API.
                    Defaults to https://api.autoppia.com or env AUTOPPIA_API_URL.
        """
        config = Configuration()
        config.host = base_url or os.getenv("AUTOPPIA_API_URL", "https://api.autoppia.com")
        self.api_client = ApiClient(configuration=config)

    def verify_jwt(self, token: str) -> Dict[str, Union[bool, str]]:
        """
        Verify an Autoppia JWT access token via the backend.

        Args:
            token (str): The JWT access token to verify.

        Returns:
            Dict[str, Union[bool, str]]: Response with verification status.
                {
                    'is_valid': bool,
                    'message': str
                }
        """
        # Use low-level call_api for parity with ApiKeyVerifier
        response = self.api_client.call_api(
            "/auth/login/jwt/verify",
            "POST",
            path_params={},
            query_params=[],
            header_params={"Content-Type": "application/json"},
            body={"token": token},
            response_type=None,
            auth_settings=[],
            _return_http_data_only=False,
            _preload_content=False,
        )

        try:
            if response.status == 200:
                # SimpleJWT verify returns 200 with empty body; normalize
                return {"is_valid": True, "message": "Valid JWT"}
            elif response.status in (400, 401):
                # Attempt to parse error body, but default message if empty
                msg = "Invalid or expired JWT"
                try:
                    if response.data:
                        data = json.loads(response.data.decode("utf-8"))
                        msg = data.get("detail") or msg
                except Exception:
                    pass
                return {"is_valid": False, "message": msg}
            else:
                err = requests.Response()
                err.status_code = response.status
                err.raw = response
                err.raise_for_status()
        except requests.exceptions.HTTPError as e:
            code = getattr(e.response, "status_code", None)
            if code in (400, 401):
                return {"is_valid": False, "message": "Invalid or expired JWT"}
            raise