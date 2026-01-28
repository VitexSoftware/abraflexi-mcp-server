#!/usr/bin/env python3
"""
Startup script for AbraFlexi MCP Server

This script validates the environment configuration and starts the MCP server
with proper error handling and logging.

Author: Vítězslav Dvořák
License: MIT
"""

import os
import sys
import logging
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def setup_logging() -> None:
    """Setup logging configuration."""
    log_level = logging.DEBUG if os.getenv("DEBUG") else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def check_environment() -> bool:
    """Check if required environment variables are set.
    
    Returns:
        bool: True if environment is properly configured
    """
    logger = logging.getLogger(__name__)
    required_vars = ["ABRAFLEXI_URL", "ABRAFLEXI_COMPANY"]
    missing_vars: List[str] = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these variables or create a .env file")
        return False
    
    # Check authentication configuration
    session_id = os.getenv("ABRAFLEXI_AUTHSESSID")
    user = os.getenv("ABRAFLEXI_LOGIN")
    password = os.getenv("ABRAFLEXI_PASSWORD")
    
    if not session_id and not (user and password):
        logger.error("Authentication not configured")
        print("Error: Authentication not configured")
        print("Please set either:")
        print("  - ABRAFLEXI_AUTHSESSID (session ID)")
        print("  - Both ABRAFLEXI_LOGIN and ABRAFLEXI_PASSWORD")
        return False
    
    # Check transport configuration
    transport = os.getenv("ABRAFLEXI_MCP_TRANSPORT", "stdio").lower()
    if transport not in ["stdio", "streamable-http"]:
        logger.error(f"Invalid ABRAFLEXI_MCP_TRANSPORT: {transport}")
        print(f"Error: Invalid ABRAFLEXI_MCP_TRANSPORT: {transport}")
        print("Valid values are: stdio, streamable-http")
        return False
    
    if transport == "streamable-http":
        auth_type = os.getenv("AUTH_TYPE", "").lower()
        if auth_type != "no-auth":
            logger.error("AUTH_TYPE must be 'no-auth' for streamable-http transport")
            print("Error: AUTH_TYPE must be set to 'no-auth' when using streamable-http transport")
            return False
    
    return True


def show_configuration() -> None:
    """Display current configuration."""
    logger = logging.getLogger(__name__)
    
    print("\n" + "=" * 50)
    print("AbraFlexi MCP Server Configuration")
    print("=" * 50)
    
    # AbraFlexi URL
    abraflexi_url = os.getenv('ABRAFLEXI_URL', 'Not configured')
    print(f"AbraFlexi URL: {abraflexi_url}")
    logger.info(f"AbraFlexi URL: {abraflexi_url}")
    
    # Company
    company = os.getenv('ABRAFLEXI_COMPANY', 'Not configured')
    print(f"Company: {company}")
    logger.info(f"Company: {company}")
    
    # Authentication method
    if os.getenv('ABRAFLEXI_AUTHSESSID'):
        auth_method = 'Session ID'
        logger.info("Authentication: Session ID")
    elif os.getenv('ABRAFLEXI_LOGIN'):
        auth_method = f"Username/Password ({os.getenv('ABRAFLEXI_LOGIN')})"
        logger.info(f"Authentication: Username/Password for user {os.getenv('ABRAFLEXI_LOGIN')}")
    else:
        auth_method = 'Not configured'
        logger.warning("Authentication: Not configured")
    
    print(f"Authentication: {auth_method}")
    
    # Transport configuration
    transport = os.getenv('ABRAFLEXI_MCP_TRANSPORT', 'stdio')
    print(f"Transport: {transport}")
    logger.info(f"Transport: {transport}")
    
    if transport == 'streamable-http':
        host = os.getenv('ABRAFLEXI_MCP_HOST', '127.0.0.1')
        port = os.getenv('ABRAFLEXI_MCP_PORT', '8000')
        stateless = os.getenv('ABRAFLEXI_MCP_STATELESS_HTTP', 'false')
        auth_type = os.getenv('AUTH_TYPE', 'Not set')
        
        print(f"  - Host: {host}")
        print(f"  - Port: {port}")
        print(f"  - Stateless: {stateless}")
        print(f"  - Auth Type: {auth_type}")
        
        logger.info(f"HTTP Transport - Host: {host}, Port: {port}, Stateless: {stateless}, Auth: {auth_type}")
    
    # Read-only mode
    read_only = os.getenv('READ_ONLY', 'true').lower() in ('true', '1', 'yes')
    read_only_str = 'Enabled' if read_only else 'Disabled'
    print(f"Read-only mode: {read_only_str}")
    logger.info(f"Read-only mode: {read_only_str}")
    
    # Timeout
    timeout = os.getenv('ABRAFLEXI_TIMEOUT', '300')
    print(f"Timeout: {timeout}s")
    logger.info(f"Timeout: {timeout}s")
    
    # Debug mode
    debug_mode = os.getenv('DEBUG', 'false').lower() in ('true', '1', 'yes')
    debug_str = 'Enabled' if debug_mode else 'Disabled'
    print(f"Debug mode: {debug_str}")
    logger.info(f"Debug mode: {debug_str}")
    
    print("=" * 50)
    print()


def main() -> None:
    """Main startup function."""
    # Setup logging first
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("Starting AbraFlexi MCP Server...")
    logger.info("Starting AbraFlexi MCP Server")
    
    try:
        # Check environment configuration
        if not check_environment():
            logger.error("Environment validation failed")
            sys.exit(1)
        
        # Show configuration
        show_configuration()
        
        # Import and run the server
        logger.info("Importing server module")
        from abraflexi_mcp_server import main as server_main
        
        logger.info("Starting MCP server")
        print("🚀 Starting MCP server...")
        print("Press Ctrl+C to stop")
        print()
        
        server_main()
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        print(f"Error importing server: {e}")
        print("Please install dependencies: uv sync")
        sys.exit(1)
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        print("\n👋 Server stopped by user")
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
