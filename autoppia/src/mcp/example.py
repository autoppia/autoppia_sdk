"""
Example usage of the MCP server and toolkit classes.

This module demonstrates how to use the MCP server and toolkit classes to interact
with the Autoppia SDK integrations.
"""

import asyncio
from autoppia.src.integrations.config import IntegrationConfig
from autoppia.src.mcp import AutoppiaIntegrationServer, EmailToolkit, ApiToolkit


def create_example_config():
    """
    Create an example configuration for the MCP server.
    
    This function creates a mock worker configuration that can be used to initialize
    the MCP server for testing purposes.
    
    Returns:
        A mock worker configuration
    """
    # Create a mock worker configuration DTO
    class MockWorkerConfigDTO:
        def __init__(self):
            self.user_integration = []
            
    # Create a mock integration DTO for email
    class MockEmailIntegrationDTO:
        def __init__(self):
            self.integration_obj = type('obj', (), {
                'name': 'Smtp',
                'category': 'email'
            })
            self.user_integration_attributes = []
            
    # Create a mock integration DTO for API
    class MockApiIntegrationDTO:
        def __init__(self):
            self.integration_obj = type('obj', (), {
                'name': 'API',
                'category': 'api'
            })
            self.user_integration_attributes = []
            
    # Create a mock attribute DTO
    class MockAttributeDTO:
        def __init__(self, name, value):
            self.integration_attribute_obj = type('obj', (), {'name': name})
            self.value = value
            self.credential_obj = None
            
    # Create the mock worker configuration
    worker_config = MockWorkerConfigDTO()
    
    # Add email integration
    email_integration = MockEmailIntegrationDTO()
    email_integration.user_integration_attributes = [
        MockAttributeDTO('SMTP Server', 'smtp.example.com'),
        MockAttributeDTO('SMTP Port', 587),
        MockAttributeDTO('IMAP Server', 'imap.example.com'),
        MockAttributeDTO('IMAP Port', 993),
        MockAttributeDTO('email', 'user@example.com'),
        MockAttributeDTO('password', 'password123')
    ]
    worker_config.user_integration.append(email_integration)
    
    # Add API integration
    api_integration = MockApiIntegrationDTO()
    api_integration.user_integration_attributes = [
        MockAttributeDTO('api_key', 'api_key_123'),
        MockAttributeDTO('domain_url', 'https://api.example.com')
    ]
    worker_config.user_integration.append(api_integration)
    
    return worker_config


async def run_server(mcp_server):
    """
    Run the MCP server.
    
    Args:
        mcp_server: The MCP server to run
    """
    await mcp_server.run()


def main():
    """
    Main function that demonstrates how to use the MCP server and toolkit classes.
    """
    try:
        print("Creating mock worker configuration...")
        worker_config = create_example_config()
        
        print("Initializing MCP server...")
        mcp_server = AutoppiaIntegrationServer(worker_config)
        
        print("Creating toolkit instances...")
        email_toolkit = EmailToolkit(mcp_server)
        api_toolkit = ApiToolkit(mcp_server)
        
        # Use the email toolkit
        print("\nSending email...")
        try:
            result = email_toolkit.send_email(
                to="recipient@example.com",
                subject="Test Email",
                body="This is a test email"
            )
            print(f"Email result: {result}")
        except Exception as e:
            print(f"Error sending email: {e}")
            import traceback
            traceback.print_exc()
        
        # Use the API toolkit
        print("\nCalling API endpoint...")
        try:
            result = api_toolkit.call_endpoint(
                url="/users",
                method="get"
            )
            print(f"API result: {result}")
        except Exception as e:
            print(f"Error calling API endpoint: {e}")
            import traceback
            traceback.print_exc()
        
        # Start the MCP server (this would normally be done in a separate process)
        print("\nStarting MCP server...")
        asyncio.run(run_server(mcp_server))
    except Exception as e:
        print(f"Error in main function: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
