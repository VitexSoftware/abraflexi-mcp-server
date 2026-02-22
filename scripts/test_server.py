#!/usr/bin/env python3
"""
Test script for AbraFlexi MCP Server

This script tests MCP tool registration, parameter signatures,
and the connection to AbraFlexi, validating basic functionality.

Author: Vítězslav Dvořák
License: MIT
"""

import os
import sys
import inspect
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from python_abraflexi import ReadOnly, ReadWrite


def test_connection():
    """Test connection to AbraFlexi server."""
    print("=" * 60)
    print("AbraFlexi MCP Server - Connection Test")
    print("=" * 60)
    print()
    
    # Get configuration
    url = os.getenv("ABRAFLEXI_URL")
    company = os.getenv("ABRAFLEXI_COMPANY")
    user = os.getenv("ABRAFLEXI_LOGIN")
    password = os.getenv("ABRAFLEXI_PASSWORD")
    
    if not url or not company:
        print("❌ Error: ABRAFLEXI_URL and ABRAFLEXI_COMPANY must be set")
        return False
    
    if not (user and password):
        print("❌ Error: ABRAFLEXI_LOGIN and ABRAFLEXI_PASSWORD must be set")
        return False
    
    print(f"Testing connection to: {url}")
    print(f"Company: {company}")
    print(f"User: {user}")
    print()
    
    try:
        # Test connection with company info (evidence=None)
        print("1. Testing basic connection (company info)...")
        client = ReadOnly(None, {
            'url': url,
            'company': company,
            'user': user,
            'password': password,
            'evidence': None
        })
        
        result = client.perform_request()
        if result:
            print("   ✓ Connection successful!")
        else:
            print("   ❌ Connection failed - no data returned")
            return False
        
        # Test invoice evidence
        print("\n2. Testing invoice evidence (faktura-vydana)...")
        invoice_client = ReadOnly(None, {
            'url': url,
            'company': company,
            'user': user,
            'password': password,
            'evidence': 'faktura-vydana'
        })
        invoice_client.default_url_params['limit'] = 5
        invoices = invoice_client.get_all_from_abraflexi()
        
        if invoices:
            print(f"   ✓ Retrieved {len(invoices)} invoices")
        else:
            print("   ✓ No invoices found (or empty result)")
        
        # Test contact evidence
        print("\n3. Testing contact evidence (adresar)...")
        contact_client = ReadOnly(None, {
            'url': url,
            'company': company,
            'user': user,
            'password': password,
            'evidence': 'adresar'
        })
        contact_client.default_url_params['limit'] = 5
        contacts = contact_client.get_all_from_abraflexi()
        
        if contacts:
            print(f"   ✓ Retrieved {len(contacts)} contacts")
        else:
            print("   ✓ No contacts found (or empty result)")
        
        # Test read-only mode
        print("\n4. Testing read-only mode...")
        read_only = os.getenv('READ_ONLY', 'true').lower() in ('true', '1', 'yes')
        if read_only:
            print("   ✓ Read-only mode is ENABLED (write operations blocked)")
        else:
            print("   ⚠ Read-only mode is DISABLED (write operations allowed)")
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_write_operations():
    """Test write operations (only if read-only mode is disabled)."""
    read_only = os.getenv('READ_ONLY', 'true').lower() in ('true', '1', 'yes')
    
    if read_only:
        print("\nℹ️  Skipping write operation tests (read-only mode enabled)")
        return True
    
    print("\n" + "=" * 60)
    print("Testing Write Operations")
    print("=" * 60)
    
    url = os.getenv("ABRAFLEXI_URL")
    company = os.getenv("ABRAFLEXI_COMPANY")
    user = os.getenv("ABRAFLEXI_LOGIN")
    password = os.getenv("ABRAFLEXI_PASSWORD")
    
    try:
        print("\n⚠️  Warning: This will create test data in your AbraFlexi instance")
        print("Press Ctrl+C to cancel, or Enter to continue...")
        input()
        
        # Test creating a contact
        print("\n1. Creating test contact...")
        client = ReadWrite(None, {
            'url': url,
            'company': company,
            'user': user,
            'password': password,
            'evidence': 'adresar'
        })
        
        import time
        test_kod = f"TEST_{int(time.time())}"
        
        client.set_data_value('kod', test_kod)
        client.set_data_value('nazev', 'Test Contact - MCP Server')
        
        result = client.insert_to_abraflexi()
        
        if result:
            print(f"   ✓ Contact created with ID: {client.last_inserted_id}")
            
            # Try to delete it
            print("\n2. Deleting test contact...")
            delete_result = client.delete()
            if delete_result:
                print("   ✓ Contact deleted successfully")
            else:
                print("   ❌ Failed to delete contact")
        else:
            print("   ❌ Failed to create contact")
            return False
        
        print("\n✅ Write operation tests passed!")
        return True
        
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        return True
    except Exception as e:
        print(f"\n❌ Write test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mcp_tools():
    """Test that all MCP tools register correctly and have valid signatures."""
    print("=" * 60)
    print("AbraFlexi MCP Server - Tool Registration Test")
    print("=" * 60)
    print()

    try:
        from abraflexi_mcp_server.server import mcp

        tools = mcp._tool_manager._tools
        print(f"   ✓ Server module imported successfully")
        print(f"   ✓ {len(tools)} tools registered")
        print()

        expected_tools = [
            "invoice_issued_get", "invoice_issued_create",
            "invoice_issued_update", "invoice_issued_delete",
            "invoice_received_get", "invoice_received_create",
            "contact_get", "contact_create",
            "contact_update", "contact_delete",
            "product_get", "product_create",
            "product_update", "product_delete",
            "bank_transaction_get", "bank_transaction_create",
            "evidence_get", "evidence_create",
            "evidence_update", "evidence_delete",
            "evidence_list",
        ]

        missing = [t for t in expected_tools if t not in tools]
        if missing:
            print(f"   ❌ Missing tools: {', '.join(missing)}")
            return False
        print(f"   ✓ All {len(expected_tools)} expected tools present")

        # Verify no **kwargs in any tool function (FastMCP forbids it)
        print()
        print("Checking tool signatures (no **kwargs allowed)...")
        for name, tool in tools.items():
            fn = tool.fn
            sig = inspect.signature(fn)
            for param in sig.parameters.values():
                if param.kind == inspect.Parameter.VAR_KEYWORD:
                    print(f"   ❌ {name} still has **kwargs")
                    return False
            print(f"   ✓ {name}")

        # Verify create/update tools accept extra_fields or data dict
        print()
        print("Checking extra_fields / data parameter on write tools...")
        create_tools = {
            "invoice_issued_create": "extra_fields",
            "invoice_received_create": "extra_fields",
            "contact_create": "extra_fields",
            "product_create": "extra_fields",
            "bank_transaction_create": "extra_fields",
        }
        update_tools = {
            "invoice_issued_update": "data",
            "contact_update": "data",
            "product_update": "data",
            "evidence_update": "data",
        }
        for name, param_name in {**create_tools, **update_tools}.items():
            fn = tools[name].fn
            sig = inspect.signature(fn)
            if param_name not in sig.parameters:
                print(f"   ❌ {name} missing '{param_name}' parameter")
                return False
            print(f"   ✓ {name} has '{param_name}'")

        print()
        print("✅ All tool registration tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Tool test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    tool_success = test_mcp_tools()
    print()
    conn_success = test_connection()

    if conn_success:
        test_write_operations()

    sys.exit(0 if (tool_success and conn_success) else 1)
