"""
MCP tools for email integration.

This module provides MCP tools that expose the functionality of the email integration.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any

from autoppia_sdk.src.mcp.server import AutoppiaIntegrationServer


class EmailToolkit:
    """
    Toolkit for email operations using MCP server.
    
    This class provides a high-level interface for email operations using the MCP server.
    It wraps the MCP server's email tools and provides a more convenient interface.
    """
    
    def __init__(self, mcp_server: AutoppiaIntegrationServer):
        """
        Initialize the email toolkit.
        
        Args:
            mcp_server: The MCP server to use for email operations
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
        
    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        files: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Send an email.
        
        Args:
            to: The recipient's email address
            subject: The subject of the email
            body: The body of the email
            html_body: The HTML body of the email (optional)
            files: A list of file paths to attach to the email (optional)
            
        Returns:
            A success message if the email was sent successfully, None otherwise
        """
        args = {
            "to": to,
            "subject": subject,
            "body": body
        }
        
        if html_body:
            args["html_body"] = html_body
            
        if files:
            args["files"] = files
            
        try:
            result = asyncio.run(self._call_tool("email.send", args))
            
            # Extract the text from the result
            if result and "content" in result and result["content"]:
                for content in result["content"]:
                    if content["type"] == "text":
                        return content["text"]
        except Exception as e:
            print(f"Error sending email: {e}")
            
        return None
        
    def read_emails(self, num: int = 5) -> Optional[List[Dict[str, str]]]:
        """
        Read emails.
        
        Args:
            num: The number of emails to read
            
        Returns:
            A list of email dictionaries if successful, None otherwise
        """
        args = {"num": num}
        
        try:
            result = asyncio.run(self._call_tool("email.read", args))
            
            # Extract the text from the result and parse it as JSON
            if result and "content" in result and result["content"]:
                for content in result["content"]:
                    if content["type"] == "text":
                        try:
                            return json.loads(content["text"])
                        except Exception as e:
                            print(f"Error parsing email result: {e}")
                            return None
        except Exception as e:
            print(f"Error reading emails: {e}")
            
        return None
