# MCP Setup Guide

This guide explains how to integrate the AbraFlexi MCP Server with MCP-compatible clients.

## Claude Desktop Integration

### Prerequisites

- Claude Desktop application installed
- AbraFlexi MCP Server installed and configured

### Configuration Steps

1. **Locate Claude Desktop Configuration**

   The configuration file is located at:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. **Add AbraFlexi MCP Server**

   Edit the configuration file and add the server to the `mcpServers` section:

   ```json
   {
     "mcpServers": {
       "abraflexi": {
         "command": "uv",
         "args": [
           "run",
           "python",
           "/home/vitex/Projects/VitexSoftware/abraflexi-mcp-server/src/abraflexi_mcp_server.py"
         ],
         "env": {
           "ABRAFLEXI_URL": "https://demo.flexibee.eu:5434",
           "ABRAFLEXI_COMPANY": "demo_de",
           "ABRAFLEXI_LOGIN": "winstrom",
           "ABRAFLEXI_PASSWORD": "winstrom",
           "READ_ONLY": "true"
         }
       }
     }
   }
   ```

   **Important Notes:**
   - Replace the path with your actual installation path
   - Update the environment variables with your AbraFlexi credentials
   - Keep `READ_ONLY: "true"` for safety (change to `"false"` only if needed)

3. **Alternative: Using .env File**

   If you prefer to use a `.env` file for configuration:

   ```json
   {
     "mcpServers": {
       "abraflexi": {
         "command": "uv",
         "args": [
           "run",
           "python",
           "/home/vitex/Projects/VitexSoftware/abraflexi-mcp-server/src/abraflexi_mcp_server.py"
         ],
         "cwd": "/home/vitex/Projects/VitexSoftware/abraflexi-mcp-server"
       }
     }
   }
   ```

   Make sure your `.env` file is in the project directory with all required variables.

4. **Restart Claude Desktop**

   Close and reopen Claude Desktop for the changes to take effect.

5. **Verify Integration**

   In Claude Desktop, you should now be able to:
   - Ask Claude to query AbraFlexi data
   - Request invoice information
   - Search for contacts and products
   - View bank transactions

   Example prompts:
   - "Show me the latest 5 issued invoices from AbraFlexi"
   - "Find all contacts with 'Example' in their name"
   - "List all available evidences in AbraFlexi"

## Using with Other MCP Clients

### Generic MCP Client Configuration

For other MCP-compatible clients, you'll need to:

1. **STDIO Transport (Default)**
   
   Run the server as a subprocess:
   ```bash
   uv run python /path/to/abraflexi-mcp-server/src/abraflexi_mcp_server.py
   ```

2. **HTTP Transport**

   Configure the server for HTTP:
   ```bash
   export ABRAFLEXI_MCP_TRANSPORT=streamable-http
   export ABRAFLEXI_MCP_HOST=127.0.0.1
   export ABRAFLEXI_MCP_PORT=8000
   export AUTH_TYPE=no-auth
   
   uv run python /path/to/abraflexi-mcp-server/src/abraflexi_mcp_server.py
   ```

   Then connect your MCP client to `http://127.0.0.1:8000`

## Available Tools

Once integrated, the following tools are available:

### Invoice Tools
- `invoice_issued_get` - Get issued invoices
- `invoice_issued_create` - Create issued invoice
- `invoice_issued_update` - Update issued invoice
- `invoice_issued_delete` - Delete issued invoice
- `invoice_received_get` - Get received invoices
- `invoice_received_create` - Create received invoice

### Contact Tools
- `contact_get` - Get contacts/companies
- `contact_create` - Create contact
- `contact_update` - Update contact
- `contact_delete` - Delete contact

### Product Tools
- `product_get` - Get products
- `product_create` - Create product
- `product_update` - Update product
- `product_delete` - Delete product

### Bank Transaction Tools
- `bank_transaction_get` - Get bank transactions
- `bank_transaction_create` - Create bank transaction

### Generic Tools
- `evidence_get` - Query any evidence
- `evidence_create` - Create record in any evidence
- `evidence_update` - Update record in any evidence
- `evidence_delete` - Delete record from any evidence
- `evidence_list` - List all available evidences

## Security Best Practices

1. **Read-Only Mode**
   - Always start with `READ_ONLY=true`
   - Only disable for specific write operations
   - Re-enable after completing write tasks

2. **Credentials**
   - Never hardcode credentials in configuration files
   - Use environment variables or `.env` files
   - Ensure `.env` files are in `.gitignore`
   - Set proper file permissions (600) on `.env` files

3. **Network Security**
   - Use HTTPS for AbraFlexi connections
   - For HTTP transport, use localhost only or secure the connection
   - Consider using VPN for remote AbraFlexi access

## Troubleshooting

### Server Not Starting

1. Check Claude Desktop logs:
   - **macOS**: `~/Library/Logs/Claude/mcp*.log`
   - **Windows**: `%APPDATA%\Claude\Logs\mcp*.log`
   - **Linux**: `~/.config/Claude/logs/mcp*.log`

2. Verify configuration:
   ```bash
   uv run python scripts/test_server.py
   ```

3. Check environment variables are set correctly

### Tools Not Appearing

1. Restart Claude Desktop completely
2. Verify the server path in configuration is correct
3. Check that `uv` is in your PATH
4. Try running the server manually to see error messages

### Connection Errors

1. Verify AbraFlexi URL is accessible
2. Check credentials are correct
3. Ensure AbraFlexi API is enabled
4. Check firewall settings

### Permission Errors

1. Verify read-only mode setting
2. Check AbraFlexi user permissions
3. Ensure the user has access to the specified company

## Example Usage in Claude Desktop

Once configured, you can interact with AbraFlexi naturally:

**User:** "Show me the latest 10 issued invoices"

**Claude:** *Uses `invoice_issued_get` tool with limit=10*

**User:** "Find contacts with 'Smith' in the name"

**Claude:** *Uses `contact_get` tool with nazev="Smith"*

**User:** "What evidences are available?"

**Claude:** *Uses `evidence_list` tool*

**User:** "Create a new contact for ABC Company"

**Claude:** *If READ_ONLY=false, uses `contact_create` tool*

## Advanced Configuration

### Multiple AbraFlexi Instances

You can configure multiple AbraFlexi servers:

```json
{
  "mcpServers": {
    "abraflexi-production": {
      "command": "uv",
      "args": ["run", "python", "/path/to/abraflexi-mcp-server/src/abraflexi_mcp_server.py"],
      "env": {
        "ABRAFLEXI_URL": "https://production.example.com",
        "ABRAFLEXI_COMPANY": "main",
        "ABRAFLEXI_LOGIN": "user",
        "ABRAFLEXI_PASSWORD": "pass",
        "READ_ONLY": "true"
      }
    },
    "abraflexi-testing": {
      "command": "uv",
      "args": ["run", "python", "/path/to/abraflexi-mcp-server/src/abraflexi_mcp_server.py"],
      "env": {
        "ABRAFLEXI_URL": "https://testing.example.com",
        "ABRAFLEXI_COMPANY": "test",
        "ABRAFLEXI_LOGIN": "testuser",
        "ABRAFLEXI_PASSWORD": "testpass",
        "READ_ONLY": "false"
      }
    }
  }
}
```

## Support

For issues or questions:
- Check the [main README](README.md)
- Review [AbraFlexi API Documentation](https://www.abraflexi.eu/api/dokumentace/)
- Open an issue on GitHub
