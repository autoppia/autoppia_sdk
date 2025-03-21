"""
MCP tools for API integration.

This module provides MCP tools that expose the functionality of the API integration.
"""

import asyncio
import json
from typing import Dict, Any, Optional, Union

from autoppia_sdk.src.mcp.server import AutoppiaIntegrationServer


class ApiToolkit:
    """
    Toolkit for API operations using MCP server.
    
    This class provides a high-level interface for API operations using the MCP server.
    It wraps the MCP server's API tools and provides a more convenient interface.
    """
    
    def __init__(self, mcp_server: AutoppiaIntegrationServer):
        """
        Initialize the API toolkit.
        
        Args:
            mcp_server: The MCP server to use for API operations
        """
        self.mcp_server = mcp_server
        
    async def _call_tool(self, name: str, arguments: Dict[str, Any]):
        """
        Call a tool on the MCP server.
        
        Args:
            name: The name of the tool to call
            arguments: The arguments to pass to the tool
            
        Returns:
            The result of the tool call
            
        Raises:
            Exception: If an error occurs
        """
        request = type('obj', (), {
            'params': type('obj', (), {
                'name': name,
                'arguments': arguments
            })
        })
        
        return await self.mcp_server.handle_call_tool(request)
        
    def call_endpoint(
        self,
        url: str,
        method: str,
        payload: Optional[Dict[str, Any]] = None
    ) -> Union[Dict[str, Any], str, None]:
        """
        Call an API endpoint.
        
        Args:
            url: The URL of the endpoint to call
            method: The HTTP method to use (get, post, put, patch, delete)
            payload: The payload to send with the request (optional)
            
        Returns:
            The response from the API endpoint, or None if an error occurred
        """
        args = {
            "url": url,
            "method": method
        }
        
        if payload:
            args["payload"] = payload
            
        try:
            result = asyncio.run(self._call_tool("api.call", args))
            
            # Extract the text from the result and parse it if possible
            if result and "content" in result and result["content"]:
                for content in result["content"]:
                    if content["type"] == "text":
                        try:
                            # Try to parse as JSON
                            return json.loads(content["text"])
                        except json.JSONDecodeError:
                            # Return as string if not valid JSON
                            return content["text"]
        except Exception as e:
            print(f"Error calling API endpoint: {e}")
                    
        return None
