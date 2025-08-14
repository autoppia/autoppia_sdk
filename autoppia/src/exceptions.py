"""
Exception classes for Autoppia SDK

This module provides custom exception classes for different types of errors
that can occur when using the SDK.
"""

from typing import Optional, Any, Dict


class AutoppiaError(Exception):
    """Base exception class for all Autoppia SDK errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ConfigurationError(AutoppiaError):
    """Raised when there's a configuration-related error."""
    pass


class AuthenticationError(AutoppiaError):
    """Raised when authentication fails."""
    pass


class APIError(AutoppiaError):
    """Raised when an API request fails."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="API_ERROR")
        self.status_code = status_code
        self.response = response


class WorkerError(AutoppiaError):
    """Raised when there's an error with worker operations."""
    pass


class WorkerStartupError(WorkerError):
    """Raised when a worker fails to start."""
    pass


class WorkerExecutionError(WorkerError):
    """Raised when a worker encounters an error during execution."""
    pass


class LLMError(AutoppiaError):
    """Raised when there's an error with LLM services."""
    pass


class LLMServiceError(LLMError):
    """Raised when an LLM service fails."""
    pass


class LLMConfigurationError(LLMError):
    """Raised when LLM configuration is invalid."""
    pass


class IntegrationError(AutoppiaError):
    """Raised when there's an error with integrations."""
    pass


class IntegrationConfigurationError(IntegrationError):
    """Raised when integration configuration is invalid."""
    pass


class IntegrationConnectionError(IntegrationError):
    """Raised when an integration fails to connect."""
    pass


class ValidationError(AutoppiaError):
    """Raised when input validation fails."""
    pass


class TimeoutError(AutoppiaError):
    """Raised when an operation times out."""
    pass


class ResourceNotFoundError(AutoppiaError):
    """Raised when a requested resource is not found."""
    pass


class RateLimitError(AutoppiaError):
    """Raised when rate limits are exceeded."""
    pass


class NetworkError(AutoppiaError):
    """Raised when there's a network-related error."""
    pass


class SerializationError(AutoppiaError):
    """Raised when serialization/deserialization fails."""
    pass


def handle_api_error(status_code: int, response: Dict[str, Any]) -> APIError:
    """Create an appropriate APIError based on status code and response."""
    if status_code == 401:
        return AuthenticationError("Authentication failed", error_code="AUTH_FAILED")
    elif status_code == 403:
        return AuthenticationError("Access denied", error_code="ACCESS_DENIED")
    elif status_code == 404:
        return ResourceNotFoundError("Resource not found", error_code="NOT_FOUND")
    elif status_code == 429:
        return RateLimitError("Rate limit exceeded", error_code="RATE_LIMIT")
    elif status_code >= 500:
        return APIError("Server error", status_code=status_code, response=response)
    else:
        return APIError(f"API request failed with status {status_code}", status_code=status_code, response=response)
