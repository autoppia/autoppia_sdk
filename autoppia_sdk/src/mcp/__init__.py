"""
MCP (Model Context Protocol) server implementation for Autoppia SDK integrations.

This module provides an MCP server that exposes the functionality of the Autoppia SDK
integrations (email, API, database, web search) as MCP tools and resources.
"""

from autoppia_sdk.src.mcp.server import AutoppiaIntegrationServer
from autoppia_sdk.src.mcp.tools import EmailToolkit, ApiToolkit

__all__ = ["AutoppiaIntegrationServer", "EmailToolkit", "ApiToolkit"]
