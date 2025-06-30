"""
MCP server implementation for Autoppia SDK integrations.

This module provides an MCP server that exposes the functionality of the Autoppia SDK
integrations (email, API, database, web search) as MCP tools and resources.
"""

import json
import sys
from typing import Any, Dict, List, Optional, Union

from modelcontextprotocol.sdk import Server
from modelcontextprotocol.sdk.server.stdio import StdioServerTransport
from modelcontextprotocol.sdk.types import (
    CallToolRequestSchema,
    ErrorCode,
    ListResourcesRequestSchema,
    ListResourceTemplatesRequestSchema,
    ListToolsRequestSchema,
    McpError,
    ReadResourceRequestSchema,
)

from autoppia.src.integrations.adapter import IntegrationsAdapter


class AutoppiaIntegrationServer:
    """
    MCP server for Autoppia SDK integrations.
    
    This class provides an MCP server that exposes the functionality of the Autoppia SDK
    integrations (email, API, database, web search) as MCP tools and resources.
    """
    
    def __init__(self, config):
        """
        Initialize the Autoppia integration server.
        
        Args:
            config: The worker configuration from the backend
        """
        # Create an MCP server
        self.server = Server(
            {
                "name": "autoppia-integration-server",
                "version": "0.1.0"
            },
            {
                "capabilities": {
                    "tools": {},
                    "resources": {}
                }
            }
        )
        
        self.config = config
        self.integrations = IntegrationsAdapter().from_autoppia_backend(config)
        
        # Set up error handling
        self.server.onerror = self.handle_error
        
        # Set up request handlers
        self.setup_request_handlers()
        
    def handle_error(self, error):
        """
        Handle errors from the MCP server.
        
        Args:
            error: The error to handle
        """
        print(f"MCP server error: {error}", file=sys.stderr)
        
    def setup_request_handlers(self):
        """
        Set up the request handlers for the server.
        
        This method registers handlers for the various MCP request types.
        """
        # Set up tool request handlers
        self.server.setRequestHandler(ListToolsRequestSchema, self.handle_list_tools)
        self.server.setRequestHandler(CallToolRequestSchema, self.handle_call_tool)
        
        # Set up resource request handlers
        self.server.setRequestHandler(ListResourcesRequestSchema, self.handle_list_resources)
        self.server.setRequestHandler(ListResourceTemplatesRequestSchema, self.handle_list_resource_templates)
        self.server.setRequestHandler(ReadResourceRequestSchema, self.handle_read_resource)
        
    async def handle_list_tools(self, request):
        """
        Handle a request to list the available tools.
        
        Args:
            request: The request to handle
            
        Returns:
            A response containing the list of available tools
        """
        tools = []
        
        # Email tools
        if "email" in self.integrations:
            tools.extend(self.get_email_tools())
            
        # API tools
        if "api" in self.integrations:
            tools.extend(self.get_api_tools())
            
        # Database tools
        if "database" in self.integrations:
            tools.extend(self.get_database_tools())
            
        # Web search tools
        if "web_search" in self.integrations:
            tools.extend(self.get_web_search_tools())
            
        return {"tools": tools}
        
    def get_email_tools(self):
        """
        Get the email tools.
        
        Returns:
            A list of email tool definitions
        """
        return [
            {
                "name": "email.send",
                "description": "Send an email",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string"},
                        "subject": {"type": "string"},
                        "body": {"type": "string"},
                        "html_body": {"type": "string"},
                        "files": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["to", "subject", "body"]
                }
            },
            {
                "name": "email.read",
                "description": "Read emails",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "num": {"type": "integer", "minimum": 1}
                    }
                }
            }
        ]
        
    def get_api_tools(self):
        """
        Get the API tools.
        
        Returns:
            A list of API tool definitions
        """
        return [
            {
                "name": "api.call",
                "description": "Call an API endpoint",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"},
                        "method": {"type": "string", "enum": ["get", "post", "put", "patch", "delete"]},
                        "payload": {"type": "object"}
                    },
                    "required": ["url", "method"]
                }
            }
        ]
        
    def get_database_tools(self):
        """
        Get the database tools.
        
        Returns:
            A list of database tool definitions
        """
        # Add database tools as needed
        return []
        
    def get_web_search_tools(self):
        """
        Get the web search tools.
        
        Returns:
            A list of web search tool definitions
        """
        # Add web search tools as needed
        return []
        
    async def handle_call_tool(self, request):
        """
        Handle a request to call a tool.
        
        Args:
            request: The request to handle
            
        Returns:
            A response containing the result of the tool call
            
        Raises:
            McpError: If the tool is not found or an error occurs
        """
        tool_name = request.params.name
        arguments = request.params.arguments
        
        # Email tools
        if tool_name.startswith("email."):
            if "email" not in self.integrations:
                raise McpError(ErrorCode.MethodNotFound, "Email integration not available")
                
            if tool_name == "email.send":
                return await self.handle_email_send(arguments)
            elif tool_name == "email.read":
                return await self.handle_email_read(arguments)
                
        # API tools
        elif tool_name.startswith("api."):
            if "api" not in self.integrations:
                raise McpError(ErrorCode.MethodNotFound, "API integration not available")
                
            if tool_name == "api.call":
                return await self.handle_api_call(arguments)
                
        # Database tools
        elif tool_name.startswith("database."):
            if "database" not in self.integrations:
                raise McpError(ErrorCode.MethodNotFound, "Database integration not available")
                
            # Add database tool handlers as needed
                
        # Web search tools
        elif tool_name.startswith("web_search."):
            if "web_search" not in self.integrations:
                raise McpError(ErrorCode.MethodNotFound, "Web search integration not available")
                
            # Add web search tool handlers as needed
                
        raise McpError(ErrorCode.MethodNotFound, f"Tool not found: {tool_name}")
        
    async def handle_email_send(self, args):
        """
        Handle the email.send tool call.
        
        Args:
            args: The arguments for the tool call
            
        Returns:
            The result of the tool call
            
        Raises:
            McpError: If an error occurs
        """
        try:
            email_integration = list(self.integrations.get("email", {}).values())[0]
            
            result = email_integration.send_email(
                args["to"],
                args["subject"],
                args["body"],
                args.get("html_body"),
                args.get("files")
            )
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result or "Email sent"
                    }
                ]
            }
        except Exception as e:
            raise McpError(ErrorCode.InternalError, f"Error sending email: {str(e)}")
        
    async def handle_email_read(self, args):
        """
        Handle the email.read tool call.
        
        Args:
            args: The arguments for the tool call
            
        Returns:
            The result of the tool call
            
        Raises:
            McpError: If an error occurs
        """
        try:
            email_integration = list(self.integrations.get("email", {}).values())[0]
            
            emails = email_integration.read_emails(args.get("num", 5))
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(emails, indent=2)
                    }
                ]
            }
        except Exception as e:
            raise McpError(ErrorCode.InternalError, f"Error reading emails: {str(e)}")
        
    async def handle_api_call(self, args):
        """
        Handle the api.call tool call.
        
        Args:
            args: The arguments for the tool call
            
        Returns:
            The result of the tool call
            
        Raises:
            McpError: If an error occurs
        """
        try:
            api_integration = list(self.integrations.get("api", {}).values())[0]
            
            result = api_integration.call_endpoint(
                args["url"],
                args["method"],
                args.get("payload", {})
            )
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2) if isinstance(result, dict) else str(result)
                    }
                ]
            }
        except Exception as e:
            raise McpError(ErrorCode.InternalError, f"Error calling API endpoint: {str(e)}")
            
    async def handle_list_resources(self, request):
        """
        Handle a request to list the available resources.
        
        Args:
            request: The request to handle
            
        Returns:
            A response containing the list of available resources
        """
        # Add resources as needed
        return {"resources": []}
        
    async def handle_list_resource_templates(self, request):
        """
        Handle a request to list the available resource templates.
        
        Args:
            request: The request to handle
            
        Returns:
            A response containing the list of available resource templates
        """
        # Add resource templates as needed
        return {"resourceTemplates": []}
        
    async def handle_read_resource(self, request):
        """
        Handle a request to read a resource.
        
        Args:
            request: The request to handle
            
        Returns:
            A response containing the resource content
            
        Raises:
            McpError: If the resource is not found or an error occurs
        """
        # Add resource handlers as needed
        raise McpError(ErrorCode.InvalidRequest, f"Resource not found: {request.params.uri}")
        
    async def run(self):
        """
        Run the server.
        
        This method starts the server and listens for requests.
        """
        transport = StdioServerTransport()
        await self.server.connect(transport)
        print(f"MCP server running on stdio", file=sys.stderr)
