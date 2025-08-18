"""
Integrations for Autoppia SDK

This package provides interfaces and implementations for connecting AI workers
to external services, APIs, and systems.

Quick Start:
    from autoppia.src.integrations import IntegrationInterface, IntegrationsAdapter
    
    # Create a custom integration
    class MyIntegration(IntegrationInterface):
        def __init__(self, api_key: str):
            self.api_key = api_key
    
    # Use the adapter
    adapter = IntegrationsAdapter()
"""

from .interface import IntegrationInterface
from .adapter import IntegrationsAdapter
from .config import IntegrationConfig

__all__ = [
    "IntegrationInterface",
    "IntegrationsAdapter", 
    "IntegrationConfig",
]
