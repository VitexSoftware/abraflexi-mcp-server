#!/usr/bin/env python3
"""
Test script for AbraFlexi MCP Server

This script tests MCP tool registration, parameter signatures,
version consistency, helper functions, packaging artifacts,
and the connection to AbraFlexi.

Author: Vítězslav Dvořák
License: MIT
"""

import os
import sys
import json
import asyncio
import inspect
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from python_abraflexi import ReadOnly, ReadWrite


def _get_tools(mcp_instance):
    """Get tools dict from FastMCP using the public async API."""
    return asyncio.run(mcp_instance.get_tools())


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


def test_version_consistency():
    """Test that version strings are consistent across all project files."""
    print("=" * 60)
    print("AbraFlexi MCP Server - Version Consistency Test")
    print("=" * 60)
    print()

    from abraflexi_mcp_server import __version__

    versions = {}

    # __init__.py
    versions["__init__.py"] = __version__
    print(f"   __init__.py:   {__version__}")

    # pyproject.toml
    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    if pyproject_path.exists():
        import re
        text = pyproject_path.read_text()
        m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
        if m:
            versions["pyproject.toml"] = m.group(1)
            print(f"   pyproject.toml: {m.group(1)}")

    # setup.py
    setup_path = PROJECT_ROOT / "setup.py"
    if setup_path.exists():
        import re
        text = setup_path.read_text()
        m = re.search(r'version\s*=\s*"([^"]+)"', text)
        if m:
            versions["setup.py"] = m.group(1)
            print(f"   setup.py:      {m.group(1)}")

    # server.json
    server_json_path = PROJECT_ROOT / "server.json"
    if server_json_path.exists():
        data = json.loads(server_json_path.read_text())
        v = data.get("version", "")
        versions["server.json"] = v
        print(f"   server.json:   {v}")

    unique = set(versions.values())
    print()
    if len(unique) == 1:
        print(f"   \u2713 All {len(versions)} files report version {unique.pop()}")
        return True
    else:
        print(f"   \u274c Version mismatch detected:")
        for fname, ver in versions.items():
            print(f"      {fname}: {ver}")
        return False


def test_helpers():
    """Test helper functions (format_response, is_read_only, evidence_list)."""
    print("=" * 60)
    print("AbraFlexi MCP Server - Helper Function Tests")
    print("=" * 60)
    print()

    from abraflexi_mcp_server.server import format_response, is_read_only, mcp

    # format_response: bool
    result = format_response(True)
    parsed = json.loads(result)
    assert parsed == {"success": True}, f"Expected {{success: true}}, got {parsed}"
    print("   \u2713 format_response(True) -> {\"success\": true}")

    result = format_response(False)
    parsed = json.loads(result)
    assert parsed == {"success": False}, f"Expected {{success: false}}, got {parsed}"
    print("   \u2713 format_response(False) -> {\"success\": false}")

    # format_response: dict
    result = format_response({"id": 1, "kod": "TEST"})
    parsed = json.loads(result)
    assert parsed["id"] == 1 and parsed["kod"] == "TEST"
    print("   \u2713 format_response(dict) serialises correctly")

    # format_response: list
    result = format_response([{"a": 1}, {"b": 2}])
    parsed = json.loads(result)
    assert len(parsed) == 2
    print("   \u2713 format_response(list) serialises correctly")

    # is_read_only
    original = os.environ.get("READ_ONLY")
    try:
        os.environ["READ_ONLY"] = "true"
        assert is_read_only() is True
        print("   \u2713 is_read_only() returns True when READ_ONLY=true")

        os.environ["READ_ONLY"] = "false"
        assert is_read_only() is False
        print("   \u2713 is_read_only() returns False when READ_ONLY=false")
    finally:
        if original is not None:
            os.environ["READ_ONLY"] = original
        else:
            os.environ.pop("READ_ONLY", None)

    # evidence_list returns valid JSON with expected keys
    tools = _get_tools(mcp)
    evidence_list_fn = tools["evidence_list"].fn
    el_result = json.loads(evidence_list_fn())
    assert isinstance(el_result, list) and len(el_result) > 0
    assert all("name" in e and "description" in e for e in el_result)
    print(f"   \u2713 evidence_list() returns {len(el_result)} evidences with name+description")

    print()
    print("\u2705 All helper function tests passed!")
    return True


def test_packaging_artifacts():
    """Test that essential packaging files exist and are well-formed."""
    print("=" * 60)
    print("AbraFlexi MCP Server - Packaging Artifacts Test")
    print("=" * 60)
    print()

    ok = True

    required_files = [
        "pyproject.toml",
        "setup.py",
        "requirements.txt",
        "Containerfile",
        "server.json",
        "README.md",
        "MCP_SETUP.md",
        "AGENTS.md",
        ".env.example",
        "appimage/AppRun",
        "appimage/build-appimage.sh",
        "appimage/abraflexi-mcp-server.desktop",
        "appimage/abraflexi-mcp-server.svg",
    ]

    for rel in required_files:
        path = PROJECT_ROOT / rel
        if path.exists():
            print(f"   \u2713 {rel}")
        else:
            print(f"   \u274c {rel} NOT FOUND")
            ok = False

    # Validate server.json schema basics
    server_json = json.loads((PROJECT_ROOT / "server.json").read_text())
    for key in ("name", "version", "repository", "packages"):
        if key not in server_json:
            print(f"   \u274c server.json missing '{key}'")
            ok = False
        else:
            print(f"   \u2713 server.json has '{key}'")

    print()
    if ok:
        print("\u2705 All packaging artifact tests passed!")
    else:
        print("\u274c Some packaging artifact tests failed!")
    return ok


def test_mcp_tools():
    """Test that all MCP tools register correctly and have valid signatures."""
    print("=" * 60)
    print("AbraFlexi MCP Server - Tool Registration Test")
    print("=" * 60)
    print()

    try:
        from abraflexi_mcp_server.server import mcp

        tools = _get_tools(mcp)
        print(f"   \u2713 Server module imported successfully")
        print(f"   \u2713 {len(tools)} tools registered")
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
            print(f"   \u274c Missing tools: {', '.join(missing)}")
            return False
        print(f"   \u2713 All {len(expected_tools)} expected tools present")

        extra = [t for t in tools if t not in expected_tools]
        if extra:
            print(f"   \u26a0 Unexpected tools (not in expected list): {', '.join(extra)}")

        # Verify no **kwargs in any tool function (FastMCP forbids it)
        print()
        print("Checking tool signatures (no **kwargs allowed)...")
        for name, tool in tools.items():
            fn = tool.fn
            sig = inspect.signature(fn)
            for param in sig.parameters.values():
                if param.kind == inspect.Parameter.VAR_KEYWORD:
                    print(f"   \u274c {name} still has **kwargs")
                    return False
            print(f"   \u2713 {name}")

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
                print(f"   \u274c {name} missing '{param_name}' parameter")
                return False
            print(f"   \u2713 {name} has '{param_name}'")

        print()
        print("\u2705 All tool registration tests passed!")
        return True

    except Exception as e:
        print(f"\n\u274c Tool test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    results = []

    results.append(test_version_consistency())
    print()
    results.append(test_helpers())
    print()
    results.append(test_packaging_artifacts())
    print()
    results.append(test_mcp_tools())
    print()
    results.append(test_connection())

    if results[-1]:  # connection succeeded
        test_write_operations()

    if all(results):
        print("\n" + "=" * 60)
        print("\u2705 ALL TESTS PASSED")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("\u274c SOME TESTS FAILED")
        print("=" * 60)

    sys.exit(0 if all(results) else 1)
