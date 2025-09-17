"""
JWT verification utilities for Autoppia SDK.

Verifies browser-issued JWTs by calling the Autoppia backend verification endpoint.
"""

import os
import json
from typing import Optional, Dict, Union
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
        self.base_url = base_url or os.getenv("AUTOPPIA_API_URL", "https://api.autoppia.com")

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
        url = f"{self.base_url}/auth/login/jwt/verify"
        headers = {"Content-Type": "application/json"}
        payload = {"token": token}

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
            if response.status_code == 200:
                return {"is_valid": True, "message": "Valid JWT"}
            if response.status_code in (400, 401):
                return {"is_valid": False, "message": "Invalid or expired JWT"}
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            status_code = getattr(e.response, "status_code", None)
            if status_code in (400, 401):
                return {"is_valid": False, "message": "Invalid or expired JWT"}
            raise


