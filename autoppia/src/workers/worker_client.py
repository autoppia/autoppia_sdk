"""
WorkerClient: Secure client to interact with workers using API key verification.

This client wraps `WorkerRouter` and checks API key validity via `ApiKeyVerifier`
before allowing any interaction.
"""

from typing import Optional, Callable

from .router import WorkerRouter
from ..utils.api_key import ApiKeyVerifier


class WorkerClient:
    """Client for interacting with workers with API key enforcement."""

    def __init__(
        self,
        api_key: str,
        worker_ip: str,
        worker_port: int,
        api_base_url: Optional[str] = None,
    ) -> None:
        self.api_key = api_key
        self.worker_ip = worker_ip
        self.worker_port = worker_port
        self.api_verifier = ApiKeyVerifier(base_url=api_base_url)
        self.router = WorkerRouter(worker_ip, worker_port)

        self._ensure_valid_api_key()

    def _ensure_valid_api_key(self) -> None:
        result = self.api_verifier.verify_api_key(self.api_key)
        if not result or not result.get("is_valid"):
            message = result.get("message") if isinstance(result, dict) else "Invalid API key"
            raise PermissionError(message or "Invalid API key")

    def call(self, message: str, stream_callback: Optional[Callable[[str], None]] = None) -> str:
        """Send a message to the worker and return its response. Requires valid API key."""
        # API key was already validated on init; callers can create per-call verification if desired
        return self.router.call(message, stream_callback)

    def close(self) -> None:
        """Close underlying connections and resources."""
        self.router.close()


