"""
Command Line Interface for Autoppia SDK
"""

import argparse
import asyncio
import sys
from .src.config import SDKConfig, get_config
from .src.exceptions import AutoppiaError


def print_banner():
    """Print the Autoppia SDK banner."""
    print("🧠 Autoppia SDK - Autonomous AI Workers Platform")
    print("=" * 50)


def print_error(message: str):
    """Print an error message."""
    print(f"❌ Error: {message}", file=sys.stderr)


def print_success(message: str):
    """Print a success message."""
    print(f"✅ {message}")


async def test_connection(api_key: str):
    """Test the connection to Autoppia API."""
    try:
        from .automata.client import AutomataClient
        
        client = AutomataClient(api_key=api_key)
        print_success("Connection test completed successfully!")
        return True
        
    except Exception as e:
        print_error(f"Connection test failed: {e}")
        return False


def show_config():
    """Show current configuration."""
    try:
        config = get_config()
        print("Current SDK Configuration:")
        print(f"API Key: {'***' if config.api_key else 'Not set'}")
        print(f"Base URL: {config.base_url}")
        print(f"Log Level: {config.log_level}")
        print(f"Default LLM Provider: {config.default_llm_provider}")
        
    except Exception as e:
        print_error(f"Failed to show configuration: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Autoppia SDK CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Test connection command
    test_parser = subparsers.add_parser("test", help="Test API connection")
    test_parser.add_argument("--api-key", required=True, help="Your API key")
    
    # Show config command
    subparsers.add_parser("config", help="Show current configuration")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "test":
            asyncio.run(test_connection(args.api_key))
        elif args.command == "config":
            show_config()
            
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
    except AutoppiaError as e:
        print_error(f"Autoppia SDK error: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
