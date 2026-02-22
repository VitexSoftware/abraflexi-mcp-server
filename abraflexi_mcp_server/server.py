#!/usr/bin/env python3
"""
AbraFlexi MCP Server - Complete integration with AbraFlexi API using python-abraflexi

This server provides comprehensive access to AbraFlexi REST API functionality through
the Model Context Protocol (MCP), enabling AI assistants and other tools to
interact with AbraFlexi accounting systems.

Author: Vítězslav Dvořák
License: MIT
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional, Union
from fastmcp import FastMCP
from python_abraflexi import ReadOnly, ReadWrite
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO if os.getenv("DEBUG") else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastMCP
mcp = FastMCP("AbraFlexi MCP Server")

# Global configuration
abraflexi_config: Optional[Dict[str, Any]] = None


def get_abraflexi_config() -> Dict[str, Any]:
    """Get AbraFlexi configuration from environment variables.
    
    Returns:
        Dict: Configuration dictionary
        
    Raises:
        ValueError: If required environment variables are missing
    """
    global abraflexi_config
    
    if abraflexi_config is None:
        url = os.getenv("ABRAFLEXI_URL")
        company = os.getenv("ABRAFLEXI_COMPANY")
        
        if not url:
            raise ValueError("ABRAFLEXI_URL environment variable is required")
        if not company:
            raise ValueError("ABRAFLEXI_COMPANY environment variable is required")
        
        logger.info(f"Initializing AbraFlexi configuration for {url}/{company}")
        
        abraflexi_config = {
            "url": url,
            "company": company,
            "user": os.getenv("ABRAFLEXI_LOGIN"),
            "password": os.getenv("ABRAFLEXI_PASSWORD"),
            "authSessionId": os.getenv("ABRAFLEXI_AUTHSESSID"),
            "timeout": int(os.getenv("ABRAFLEXI_TIMEOUT", "300")),
        }
        
        # Validate authentication
        if not abraflexi_config["authSessionId"] and not (
            abraflexi_config["user"] and abraflexi_config["password"]
        ):
            raise ValueError(
                "Either ABRAFLEXI_AUTHSESSID or ABRAFLEXI_LOGIN/ABRAFLEXI_PASSWORD must be set"
            )
        
        logger.info("Successfully configured AbraFlexi connection")
    
    return abraflexi_config


def get_readonly_client(evidence: str) -> ReadOnly:
    """Create a read-only AbraFlexi client for the specified evidence.
    
    Args:
        evidence: Evidence name (e.g., 'faktura-vydana', 'adresar')
        
    Returns:
        ReadOnly: Configured AbraFlexi client
    """
    config = get_abraflexi_config()
    options = {**config, "evidence": evidence}
    return ReadOnly(None, options)


def get_readwrite_client(evidence: str) -> ReadWrite:
    """Create a read-write AbraFlexi client for the specified evidence.
    
    Args:
        evidence: Evidence name (e.g., 'faktura-vydana', 'adresar')
        
    Returns:
        ReadWrite: Configured AbraFlexi client
    """
    config = get_abraflexi_config()
    options = {**config, "evidence": evidence}
    return ReadWrite(None, options)


def is_read_only() -> bool:
    """Check if server is in read-only mode.
    
    Returns:
        bool: True if read-only mode is enabled
    """
    return os.getenv("READ_ONLY", "true").lower() in ("true", "1", "yes")


def format_response(data: Any) -> str:
    """Format response data as JSON string.
    
    Args:
        data: Data to format
        
    Returns:
        str: JSON formatted string
    """
    if isinstance(data, bool):
        return json.dumps({"success": data})
    return json.dumps(data, indent=2, default=str, ensure_ascii=False)


def validate_read_only() -> None:
    """Validate that write operations are allowed.
    
    Raises:
        ValueError: If server is in read-only mode
    """
    if is_read_only():
        raise ValueError("Server is in read-only mode - write operations are not allowed")


# ISSUED INVOICES (Faktura Vydaná)
@mcp.tool()
def invoice_issued_get(
    ids: Optional[List[str]] = None,
    kod: Optional[str] = None,
    limit: Optional[int] = None,
    detail: str = "summary"
) -> str:
    """Get issued invoices (faktura-vydana) from AbraFlexi.
    
    Args:
        ids: List of invoice IDs to retrieve
        kod: Invoice code to search for
        limit: Maximum number of results
        detail: Detail level (summary, id, full, custom:field1,field2)
        
    Returns:
        str: JSON formatted list of invoices
    """
    client = get_readonly_client("faktura-vydana")
    
    # Build filter
    filters = []
    if ids:
        filters.append(f"id in ({','.join(ids)})")
    if kod:
        filters.append(f"kod='{kod}'")
    
    if filters:
        client.filter = " AND ".join(filters)
    
    client.default_url_params["detail"] = detail
    if limit:
        client.default_url_params["limit"] = limit
    
    result = client.get_all_from_abraflexi()
    return format_response(result)


@mcp.tool()
def invoice_issued_create(
    kod: str,
    firma: str,
    datum_vystaveni: Optional[str] = None,
    polozky: Optional[List[Dict[str, Any]]] = None,
    extra_fields: Optional[Dict[str, Any]] = None
) -> str:
    """Create a new issued invoice in AbraFlexi.
    
    Args:
        kod: Invoice code (unique identifier)
        firma: Customer reference (e.g., 'code:CUSTOMER01')
        datum_vystaveni: Issue date (YYYY-MM-DD format)
        polozky: Invoice items/lines
        extra_fields: Additional invoice fields
        
    Returns:
        str: JSON formatted creation result
    """
    validate_read_only()
    
    client = get_readwrite_client("faktura-vydana")
    
    # Set required fields
    client.set_data_value("kod", kod)
    client.set_data_value("firma", firma)
    
    if datum_vystaveni:
        client.set_data_value("datVyst", datum_vystaveni)
    
    if polozky:
        client.set_data_value("polozkyFaktury", polozky)
    
    # Set additional fields
    if extra_fields:
        for key, value in extra_fields.items():
            client.set_data_value(key, value)
    
    result = client.insert_to_abraflexi()
    
    return format_response({
        "success": result,
        "id": client.last_inserted_id,
        "kod": kod
    })


@mcp.tool()
def invoice_issued_update(
    id: Optional[str] = None,
    kod: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None
) -> str:
    """Update an existing issued invoice in AbraFlexi.
    
    Args:
        id: Invoice ID to update
        kod: Invoice code to update (alternative to id)
        data: Fields to update
        
    Returns:
        str: JSON formatted update result
    """
    validate_read_only()
    
    if not id and not kod:
        raise ValueError("Either id or kod must be provided")
    
    identifier = int(id) if id else f"code:{kod}"
    client = get_readwrite_client("faktura-vydana")
    
    # Load existing invoice
    if not client.load_from_abraflexi(identifier):
        raise ValueError(f"Invoice not found: {identifier}")
    
    # Update fields
    if data:
        for key, value in data.items():
            client.set_data_value(key, value)
    
    result = client.update()
    
    return format_response({"success": result})


@mcp.tool()
def invoice_issued_delete(id: Optional[str] = None, kod: Optional[str] = None) -> str:
    """Delete an issued invoice from AbraFlexi.
    
    Args:
        id: Invoice ID to delete
        kod: Invoice code to delete (alternative to id)
        
    Returns:
        str: JSON formatted deletion result
    """
    validate_read_only()
    
    if not id and not kod:
        raise ValueError("Either id or kod must be provided")
    
    identifier = int(id) if id else f"code:{kod}"
    client = get_readwrite_client("faktura-vydana")
    
    # Load and delete
    if not client.load_from_abraflexi(identifier):
        raise ValueError(f"Invoice not found: {identifier}")
    
    result = client.delete()
    
    return format_response({"success": result})


# RECEIVED INVOICES (Faktura Přijatá)
@mcp.tool()
def invoice_received_get(
    ids: Optional[List[str]] = None,
    kod: Optional[str] = None,
    limit: Optional[int] = None,
    detail: str = "summary"
) -> str:
    """Get received invoices (faktura-prijata) from AbraFlexi.
    
    Args:
        ids: List of invoice IDs to retrieve
        kod: Invoice code to search for
        limit: Maximum number of results
        detail: Detail level (summary, id, full, custom:field1,field2)
        
    Returns:
        str: JSON formatted list of invoices
    """
    client = get_readonly_client("faktura-prijata")
    
    # Build filter
    filters = []
    if ids:
        filters.append(f"id in ({','.join(ids)})")
    if kod:
        filters.append(f"kod='{kod}'")
    
    if filters:
        client.filter = " AND ".join(filters)
    
    client.default_url_params["detail"] = detail
    if limit:
        client.default_url_params["limit"] = limit
    
    result = client.get_all_from_abraflexi()
    return format_response(result)


@mcp.tool()
def invoice_received_create(
    kod: str,
    firma: str,
    datum_vystaveni: Optional[str] = None,
    polozky: Optional[List[Dict[str, Any]]] = None,
    extra_fields: Optional[Dict[str, Any]] = None
) -> str:
    """Create a new received invoice in AbraFlexi.
    
    Args:
        kod: Invoice code (unique identifier)
        firma: Supplier reference (e.g., 'code:SUPPLIER01')
        datum_vystaveni: Issue date (YYYY-MM-DD format)
        polozky: Invoice items/lines
        extra_fields: Additional invoice fields
        
    Returns:
        str: JSON formatted creation result
    """
    validate_read_only()
    
    client = get_readwrite_client("faktura-prijata")
    
    # Set required fields
    client.set_data_value("kod", kod)
    client.set_data_value("firma", firma)
    
    if datum_vystaveni:
        client.set_data_value("datVyst", datum_vystaveni)
    
    if polozky:
        client.set_data_value("polozkyFaktury", polozky)
    
    # Set additional fields
    if extra_fields:
        for key, value in extra_fields.items():
            client.set_data_value(key, value)
    
    result = client.insert_to_abraflexi()
    
    return format_response({
        "success": result,
        "id": client.last_inserted_id,
        "kod": kod
    })


# CONTACTS/COMPANIES (Adresář)
@mcp.tool()
def contact_get(
    ids: Optional[List[str]] = None,
    kod: Optional[str] = None,
    nazev: Optional[str] = None,
    limit: Optional[int] = None,
    detail: str = "summary"
) -> str:
    """Get contacts/companies (adresar) from AbraFlexi.
    
    Args:
        ids: List of contact IDs to retrieve
        kod: Contact code to search for
        nazev: Contact name to search for (partial match)
        limit: Maximum number of results
        detail: Detail level (summary, id, full, custom:field1,field2)
        
    Returns:
        str: JSON formatted list of contacts
    """
    client = get_readonly_client("adresar")
    
    # Build filter
    filters = []
    if ids:
        filters.append(f"id in ({','.join(ids)})")
    if kod:
        filters.append(f"kod='{kod}'")
    if nazev:
        filters.append(f"nazev like '*{nazev}*'")
    
    if filters:
        client.filter = " AND ".join(filters)
    
    client.default_url_params["detail"] = detail
    if limit:
        client.default_url_params["limit"] = limit
    
    result = client.get_all_from_abraflexi()
    return format_response(result)


@mcp.tool()
def contact_create(
    kod: str,
    nazev: str,
    email: Optional[str] = None,
    tel: Optional[str] = None,
    extra_fields: Optional[Dict[str, Any]] = None
) -> str:
    """Create a new contact/company in AbraFlexi.
    
    Args:
        kod: Contact code (unique identifier)
        nazev: Contact name
        email: Email address
        tel: Phone number
        extra_fields: Additional contact fields
        
    Returns:
        str: JSON formatted creation result
    """
    validate_read_only()
    
    client = get_readwrite_client("adresar")
    
    # Set required fields
    client.set_data_value("kod", kod)
    client.set_data_value("nazev", nazev)
    
    if email:
        client.set_data_value("email", email)
    if tel:
        client.set_data_value("tel", tel)
    
    # Set additional fields
    if extra_fields:
        for key, value in extra_fields.items():
            client.set_data_value(key, value)
    
    result = client.insert_to_abraflexi()
    
    return format_response({
        "success": result,
        "id": client.last_inserted_id,
        "kod": kod
    })


@mcp.tool()
def contact_update(
    id: Optional[str] = None,
    kod: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None
) -> str:
    """Update an existing contact/company in AbraFlexi.
    
    Args:
        id: Contact ID to update
        kod: Contact code to update (alternative to id)
        data: Fields to update
        
    Returns:
        str: JSON formatted update result
    """
    validate_read_only()
    
    if not id and not kod:
        raise ValueError("Either id or kod must be provided")
    
    identifier = int(id) if id else f"code:{kod}"
    client = get_readwrite_client("adresar")
    
    # Load existing contact
    if not client.load_from_abraflexi(identifier):
        raise ValueError(f"Contact not found: {identifier}")
    
    # Update fields
    if data:
        for key, value in data.items():
            client.set_data_value(key, value)
    
    result = client.update()
    
    return format_response({"success": result})


@mcp.tool()
def contact_delete(id: Optional[str] = None, kod: Optional[str] = None) -> str:
    """Delete a contact/company from AbraFlexi.
    
    Args:
        id: Contact ID to delete
        kod: Contact code to delete (alternative to id)
        
    Returns:
        str: JSON formatted deletion result
    """
    validate_read_only()
    
    if not id and not kod:
        raise ValueError("Either id or kod must be provided")
    
    identifier = int(id) if id else f"code:{kod}"
    client = get_readwrite_client("adresar")
    
    # Load and delete
    if not client.load_from_abraflexi(identifier):
        raise ValueError(f"Contact not found: {identifier}")
    
    result = client.delete()
    
    return format_response({"success": result})


# PRODUCTS (Ceník)
@mcp.tool()
def product_get(
    ids: Optional[List[str]] = None,
    kod: Optional[str] = None,
    nazev: Optional[str] = None,
    limit: Optional[int] = None,
    detail: str = "summary"
) -> str:
    """Get products (cenik) from AbraFlexi.
    
    Args:
        ids: List of product IDs to retrieve
        kod: Product code to search for
        nazev: Product name to search for (partial match)
        limit: Maximum number of results
        detail: Detail level (summary, id, full, custom:field1,field2)
        
    Returns:
        str: JSON formatted list of products
    """
    client = get_readonly_client("cenik")
    
    # Build filter
    filters = []
    if ids:
        filters.append(f"id in ({','.join(ids)})")
    if kod:
        filters.append(f"kod='{kod}'")
    if nazev:
        filters.append(f"nazev like '*{nazev}*'")
    
    if filters:
        client.filter = " AND ".join(filters)
    
    client.default_url_params["detail"] = detail
    if limit:
        client.default_url_params["limit"] = limit
    
    result = client.get_all_from_abraflexi()
    return format_response(result)


@mcp.tool()
def product_create(
    kod: str,
    nazev: str,
    cena: Optional[float] = None,
    extra_fields: Optional[Dict[str, Any]] = None
) -> str:
    """Create a new product in AbraFlexi.
    
    Args:
        kod: Product code (unique identifier)
        nazev: Product name
        cena: Product price
        extra_fields: Additional product fields
        
    Returns:
        str: JSON formatted creation result
    """
    validate_read_only()
    
    client = get_readwrite_client("cenik")
    
    # Set required fields
    client.set_data_value("kod", kod)
    client.set_data_value("nazev", nazev)
    
    if cena is not None:
        client.set_data_value("cenaZakl", cena)
    
    # Set additional fields
    if extra_fields:
        for key, value in extra_fields.items():
            client.set_data_value(key, value)
    
    result = client.insert_to_abraflexi()
    
    return format_response({
        "success": result,
        "id": client.last_inserted_id,
        "kod": kod
    })


@mcp.tool()
def product_update(
    id: Optional[str] = None,
    kod: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None
) -> str:
    """Update an existing product in AbraFlexi.
    
    Args:
        id: Product ID to update
        kod: Product code to update (alternative to id)
        data: Fields to update
        
    Returns:
        str: JSON formatted update result
    """
    validate_read_only()
    
    if not id and not kod:
        raise ValueError("Either id or kod must be provided")
    
    identifier = int(id) if id else f"code:{kod}"
    client = get_readwrite_client("cenik")
    
    # Load existing product
    if not client.load_from_abraflexi(identifier):
        raise ValueError(f"Product not found: {identifier}")
    
    # Update fields
    if data:
        for key, value in data.items():
            client.set_data_value(key, value)
    
    result = client.update()
    
    return format_response({"success": result})


@mcp.tool()
def product_delete(id: Optional[str] = None, kod: Optional[str] = None) -> str:
    """Delete a product from AbraFlexi.
    
    Args:
        id: Product ID to delete
        kod: Product code to delete (alternative to id)
        
    Returns:
        str: JSON formatted deletion result
    """
    validate_read_only()
    
    if not id and not kod:
        raise ValueError("Either id or kod must be provided")
    
    identifier = int(id) if id else f"code:{kod}"
    client = get_readwrite_client("cenik")
    
    # Load and delete
    if not client.load_from_abraflexi(identifier):
        raise ValueError(f"Product not found: {identifier}")
    
    result = client.delete()
    
    return format_response({"success": result})


# BANK TRANSACTIONS (Banka)
@mcp.tool()
def bank_transaction_get(
    ids: Optional[List[str]] = None,
    limit: Optional[int] = None,
    detail: str = "summary"
) -> str:
    """Get bank transactions (banka) from AbraFlexi.
    
    Args:
        ids: List of transaction IDs to retrieve
        limit: Maximum number of results
        detail: Detail level (summary, id, full, custom:field1,field2)
        
    Returns:
        str: JSON formatted list of bank transactions
    """
    client = get_readonly_client("banka")
    
    # Build filter
    if ids:
        client.filter = f"id in ({','.join(ids)})"
    
    client.default_url_params["detail"] = detail
    if limit:
        client.default_url_params["limit"] = limit
    
    result = client.get_all_from_abraflexi()
    return format_response(result)


@mcp.tool()
def bank_transaction_create(
    banka: str,
    datum: str,
    castka: float,
    popis: Optional[str] = None,
    extra_fields: Optional[Dict[str, Any]] = None
) -> str:
    """Create a new bank transaction in AbraFlexi.
    
    Args:
        banka: Bank account reference (e.g., 'code:BANK01')
        datum: Transaction date (YYYY-MM-DD format)
        castka: Transaction amount
        popis: Transaction description
        extra_fields: Additional transaction fields
        
    Returns:
        str: JSON formatted creation result
    """
    validate_read_only()
    
    client = get_readwrite_client("banka")
    
    # Set required fields
    client.set_data_value("banka", banka)
    client.set_data_value("datum", datum)
    client.set_data_value("castka", castka)
    
    if popis:
        client.set_data_value("popis", popis)
    
    # Set additional fields
    if extra_fields:
        for key, value in extra_fields.items():
            client.set_data_value(key, value)
    
    result = client.insert_to_abraflexi()
    
    return format_response({
        "success": result,
        "id": client.last_inserted_id
    })


# GENERIC EVIDENCE OPERATIONS
@mcp.tool()
def evidence_get(
    evidence: str,
    ids: Optional[List[str]] = None,
    filter_expr: Optional[str] = None,
    limit: Optional[int] = None,
    detail: str = "summary"
) -> str:
    """Get records from any AbraFlexi evidence.
    
    Args:
        evidence: Evidence name (e.g., 'faktura-vydana', 'adresar', 'cenik')
        ids: List of record IDs to retrieve
        filter_expr: AbraFlexi filter expression
        limit: Maximum number of results
        detail: Detail level (summary, id, full, custom:field1,field2)
        
    Returns:
        str: JSON formatted list of records
    """
    client = get_readonly_client(evidence)
    
    # Build filter
    if ids:
        client.filter = f"id in ({','.join(ids)})"
    elif filter_expr:
        client.filter = filter_expr
    
    client.default_url_params["detail"] = detail
    if limit:
        client.default_url_params["limit"] = limit
    
    result = client.get_all_from_abraflexi()
    return format_response(result)


@mcp.tool()
def evidence_create(evidence: str, data: Dict[str, Any]) -> str:
    """Create a new record in any AbraFlexi evidence.
    
    Args:
        evidence: Evidence name (e.g., 'faktura-vydana', 'adresar', 'cenik')
        data: Record data as dictionary
        
    Returns:
        str: JSON formatted creation result
    """
    validate_read_only()
    
    client = get_readwrite_client(evidence)
    
    # Set all data fields
    for key, value in data.items():
        client.set_data_value(key, value)
    
    result = client.insert_to_abraflexi()
    
    return format_response({
        "success": result,
        "id": client.last_inserted_id
    })


@mcp.tool()
def evidence_update(
    evidence: str,
    id: Optional[str] = None,
    kod: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None
) -> str:
    """Update a record in any AbraFlexi evidence.
    
    Args:
        evidence: Evidence name (e.g., 'faktura-vydana', 'adresar', 'cenik')
        id: Record ID to update
        kod: Record code to update (alternative to id)
        data: Fields to update as dictionary
        
    Returns:
        str: JSON formatted update result
    """
    validate_read_only()
    
    if not id and not kod:
        raise ValueError("Either id or kod must be provided")
    
    identifier = int(id) if id else f"code:{kod}"
    client = get_readwrite_client(evidence)
    
    # Load existing record
    if not client.load_from_abraflexi(identifier):
        raise ValueError(f"Record not found in {evidence}: {identifier}")
    
    # Update fields
    if data:
        for key, value in data.items():
            client.set_data_value(key, value)
    
    result = client.update()
    
    return format_response({"success": result})


@mcp.tool()
def evidence_delete(
    evidence: str,
    id: Optional[str] = None,
    kod: Optional[str] = None
) -> str:
    """Delete a record from any AbraFlexi evidence.
    
    Args:
        evidence: Evidence name (e.g., 'faktura-vydana', 'adresar', 'cenik')
        id: Record ID to delete
        kod: Record code to delete (alternative to id)
        
    Returns:
        str: JSON formatted deletion result
    """
    validate_read_only()
    
    if not id and not kod:
        raise ValueError("Either id or kod must be provided")
    
    identifier = int(id) if id else f"code:{kod}"
    client = get_readwrite_client(evidence)
    
    # Load and delete
    if not client.load_from_abraflexi(identifier):
        raise ValueError(f"Record not found in {evidence}: {identifier}")
    
    result = client.delete()
    
    return format_response({"success": result})


@mcp.tool()
def evidence_list() -> str:
    """List all available AbraFlexi evidences.
    
    Returns:
        str: JSON formatted list of evidence names
    """
    # Common AbraFlexi evidences
    evidences = [
        {"name": "faktura-vydana", "description": "Issued invoices"},
        {"name": "faktura-prijata", "description": "Received invoices"},
        {"name": "adresar", "description": "Contacts and companies"},
        {"name": "cenik", "description": "Products and services"},
        {"name": "banka", "description": "Bank transactions"},
        {"name": "pokladna", "description": "Cash transactions"},
        {"name": "nabidka-vydana", "description": "Issued quotes"},
        {"name": "objednavka-vydana", "description": "Issued orders"},
        {"name": "objednavka-prijata", "description": "Received orders"},
        {"name": "dodaci-list", "description": "Delivery notes"},
        {"name": "sklad", "description": "Warehouse/stock"},
        {"name": "cenova-uroven", "description": "Price levels"},
        {"name": "typ-smlouvy", "description": "Contract types"},
    ]
    
    return format_response(evidences)


def main():
    """Main entry point for the MCP server."""
    # Get transport configuration
    transport = os.getenv("ABRAFLEXI_MCP_TRANSPORT", "stdio").lower()
    
    if transport == "streamable-http":
        # HTTP transport configuration
        host = os.getenv("ABRAFLEXI_MCP_HOST", "127.0.0.1")
        port = int(os.getenv("ABRAFLEXI_MCP_PORT", "8000"))
        stateless = os.getenv("ABRAFLEXI_MCP_STATELESS_HTTP", "false").lower() in ("true", "1", "yes")
        
        logger.info(f"Starting MCP server with HTTP transport on {host}:{port}")
        mcp.run(transport="streamable-http", host=host, port=port, stateless=stateless)
    else:
        # Default stdio transport
        logger.info("Starting MCP server with stdio transport")
        mcp.run()


if __name__ == "__main__":
    main()
