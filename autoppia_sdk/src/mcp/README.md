# MCP Server for Autoppia SDK Integrations

This module provides an MCP (Model Context Protocol) server that exposes the functionality of the Autoppia SDK integrations (email, API, database, web search) as MCP tools and resources.

## Overview

The MCP server allows you to expose the functionality of your Autoppia SDK integrations to MCP clients, such as large language models (LLMs). This enables the LLMs to interact with your integrations in a standardized way.

The module also provides toolkit classes that wrap the MCP server functionality, making it easier to use the integrations from your code.

## Components

### MCP Server

The `AutoppiaIntegrationServer` class is the main MCP server implementation. It exposes the functionality of the Autoppia SDK integrations as MCP tools and resources.

```python
import asyncio
from autoppia_sdk.src.mcp import AutoppiaIntegrationServer

# Initialize the MCP server with a worker configuration
mcp_server = AutoppiaIntegrationServer(worker_config)

# Run the server
asyncio.run(mcp_server.run())
```

### Toolkit Classes

The toolkit classes provide a high-level interface for interacting with the integrations through the MCP server.

#### EmailToolkit

The `EmailToolkit` class provides methods for sending and reading emails.

```python
from autoppia_sdk.src.mcp import EmailToolkit

# Initialize the toolkit with an MCP server
email_toolkit = EmailToolkit(mcp_server)

# Send an email
result = email_toolkit.send_email(
    to="recipient@example.com",
    subject="Test Email",
    body="This is a test email",
    html_body="<p>This is a test email</p>",
    files=["attachment.pdf"]
)

# Read emails
emails = email_toolkit.read_emails(num=5)
```

#### ApiToolkit

The `ApiToolkit` class provides methods for calling API endpoints.

```python
from autoppia_sdk.src.mcp import ApiToolkit

# Initialize the toolkit with an MCP server
api_toolkit = ApiToolkit(mcp_server)

# Call an API endpoint
result = api_toolkit.call_endpoint(
    url="/users",
    method="get"
)

# Call an API endpoint with a payload
result = api_toolkit.call_endpoint(
    url="/users",
    method="post",
    payload={"name": "John Doe", "email": "john@example.com"}
)
```

## Example Usage

See the `example.py` file for a complete example of how to use the MCP server and toolkit classes.

```python
import asyncio

# Create a worker configuration
worker_config = create_example_config()

# Initialize the MCP server
mcp_server = AutoppiaIntegrationServer(worker_config)

# Create toolkit instances
email_toolkit = EmailToolkit(mcp_server)
api_toolkit = ApiToolkit(mcp_server)

# Use the email toolkit
result = email_toolkit.send_email(
    to="recipient@example.com",
    subject="Test Email",
    body="This is a test email"
)

# Use the API toolkit
result = api_toolkit.call_endpoint(
    url="/users",
    method="get"
)

# Start the MCP server
async def run_server():
    await mcp_server.run()

asyncio.run(run_server())
```

## Installation

To use the MCP server, you need to install the MCP SDK:

```bash
pip install modelcontextprotocol
```

## Requirements

- Python 3.7 or higher
- Autoppia SDK
- MCP SDK
