# AbraFlexi MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A comprehensive Model Context Protocol (MCP) server for AbraFlexi integration using FastMCP and python-abraflexi. This server provides complete access to AbraFlexi REST API functionality through MCP-compatible tools.

## Features

### 📄 Invoice Management
- `invoice_issued_get` - Retrieve issued invoices (faktura-vydana)
- `invoice_issued_create` - Create new issued invoices
- `invoice_issued_update` - Update existing issued invoices
- `invoice_issued_delete` - Remove issued invoices
- `invoice_received_get` - Retrieve received invoices (faktura-prijata)
- `invoice_received_create` - Create new received invoices

### 👥 Contact Management
- `contact_get` - Retrieve contacts and companies (adresar)
- `contact_create` - Create new contacts
- `contact_update` - Update existing contacts
- `contact_delete` - Remove contacts

### 📦 Product Management
- `product_get` - Retrieve products from price list (cenik)
- `product_create` - Create new products
- `product_update` - Update existing products
- `product_delete` - Remove products

### 🏦 Bank Transaction Management
- `bank_transaction_get` - Retrieve bank transactions (banka)
- `bank_transaction_create` - Create new bank transactions

### 🔧 Generic Evidence Operations
- `evidence_get` - Get records from any evidence
- `evidence_create` - Create record in any evidence
- `evidence_update` - Update record in any evidence
- `evidence_delete` - Delete record from any evidence
- `evidence_list` - List all available evidences

## Installation

### Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended) or pip
- Access to an AbraFlexi server with API enabled

### Quick Start

1. **Clone or navigate to the repository:**
   ```bash
   cd /home/vitex/Projects/VitexSoftware/abraflexi-mcp-server
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```
   
   Or with pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your AbraFlexi server details
   ```

4. **Test the installation:**
   ```bash
   uv run python scripts/test_server.py
   ```

## Configuration

### Required Environment Variables

- `ABRAFLEXI_URL` - Your AbraFlexi server URL (e.g., `https://demo.flexibee.eu:5434`)
- `ABRAFLEXI_COMPANY` - Company identifier (e.g., `demo_de`)

### Authentication (choose one method)

**Method 1: Username/Password (Recommended)**
- `ABRAFLEXI_LOGIN` - Your AbraFlexi username
- `ABRAFLEXI_PASSWORD` - Your AbraFlexi password

**Method 2: Session ID**
- `ABRAFLEXI_AUTHSESSID` - Your AbraFlexi session ID

### Optional Configuration

- `READ_ONLY` - Set to `true`, `1`, or `yes` to enable read-only mode (default: `true`)
- `ABRAFLEXI_TIMEOUT` - Request timeout in seconds (default: `300`)

### Transport Configuration

- `ABRAFLEXI_MCP_TRANSPORT` - Transport type: `stdio` (default) or `streamable-http`

**HTTP Transport Configuration** (only used when `ABRAFLEXI_MCP_TRANSPORT=streamable-http`):
- `ABRAFLEXI_MCP_HOST` - Server host (default: `127.0.0.1`)
- `ABRAFLEXI_MCP_PORT` - Server port (default: `8000`)
- `ABRAFLEXI_MCP_STATELESS_HTTP` - Stateless mode (default: `false`)
- `AUTH_TYPE` - Must be set to `no-auth` for streamable-http transport

## Usage

### Running the Server

**With startup script (recommended):**
```bash
uv run python scripts/start_server.py
```

**Direct execution:**
```bash
uv run python src/abraflexi_mcp_server.py
```

### Transport Options

The server supports two transport methods:

#### STDIO Transport (Default)
Standard input/output transport for MCP clients like Claude Desktop:
```bash
# Set in .env or environment
ABRAFLEXI_MCP_TRANSPORT=stdio
```

#### HTTP Transport
HTTP-based transport for web integrations:
```bash
# Set in .env or environment
ABRAFLEXI_MCP_TRANSPORT=streamable-http
ABRAFLEXI_MCP_HOST=127.0.0.1
ABRAFLEXI_MCP_PORT=8000
ABRAFLEXI_MCP_STATELESS_HTTP=false
AUTH_TYPE=no-auth
```

### Testing

**Run test suite:**
```bash
uv run python scripts/test_server.py
```

### Read-Only Mode

When `READ_ONLY=true` (default), the server will only expose GET operations (retrieve data) and block all create, update, and delete operations. This is useful for:

- 📊 Monitoring dashboards
- 🔍 Read-only integrations
- 🔒 Security-conscious environments
- 🛡️ Preventing accidental modifications

To enable write operations, set `READ_ONLY=false` in your `.env` file.

### Example Tool Calls

**Get all issued invoices:**
```python
invoice_issued_get(limit=10)
```

**Get specific invoice by code:**
```python
invoice_issued_get(kod="INV-2024-001")
```

**Create a new contact:**
```python
contact_create(
    kod="CUSTOMER01",
    nazev="Example Company s.r.o.",
    email="info@example.com",
    tel="+420123456789"
)
```

**Get products:**
```python
product_get(nazev="Widget", limit=5)
```

**Generic evidence query:**
```python
evidence_get(
    evidence="faktura-vydana",
    filter_expr="datVyst >= '2024-01-01'",
    limit=20
)
```

## MCP Integration

This server is designed to work with MCP-compatible clients like Claude Desktop. See [MCP_SETUP.md](MCP_SETUP.md) for detailed integration instructions.

## Development

### Project Structure

```
abraflexi-mcp-server/
├── src/
│   ├── __init__.py
│   └── abraflexi_mcp_server.py    # Main server implementation
├── scripts/
│   ├── start_server.py            # Startup script with validation
│   └── test_server.py             # Test script
├── pyproject.toml                 # Python project configuration
├── requirements.txt               # Dependencies
├── .env.example                   # Environment configuration template
├── .env                           # Your configuration (not in git)
├── .gitignore                     # Git ignore patterns
└── README.md                      # This file
```

### Running Tests

```bash
# Test server functionality
uv run python scripts/test_server.py

# Test with specific environment
ABRAFLEXI_URL=https://your-server.com uv run python scripts/test_server.py
```

## Error Handling

The server includes comprehensive error handling:

- ✅ Authentication errors are clearly reported
- 🔒 Read-only mode violations are blocked with descriptive messages
- ✔️ Invalid parameters are validated
- 🌐 Network and API errors are properly formatted
- 📝 Detailed logging for troubleshooting

## Security Considerations

- 🔑 Store credentials securely in `.env` file (never commit to git)
- 🔒 Enable read-only mode for monitoring-only use cases
- 🛡️ Use HTTPS for AbraFlexi server connections
- 🔄 Regularly rotate passwords
- 📁 Ensure `.env` file has proper permissions (600)

## Troubleshooting

### Common Issues

**Connection Failed:**
- Verify `ABRAFLEXI_URL` is correct and accessible
- Check authentication credentials
- Ensure AbraFlexi API is enabled
- Check firewall/network settings

**Permission Denied:**
- Verify user has sufficient AbraFlexi permissions
- Check if read-only mode is enabled when trying to modify data

**Tool Not Found:**
- Ensure all dependencies are installed: `uv sync`
- Verify Python version compatibility (3.10+)

### Debug Mode

Set environment variable for detailed logging:
```bash
export DEBUG=1
uv run python scripts/start_server.py
```

## Dependencies

- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [python-abraflexi](https://github.com/VitexSoftware/python-abraflexi) - AbraFlexi Python library
- [python-dotenv](https://github.com/theskumar/python-dotenv) - Environment variable management

## License

This project is licensed under the MIT License.

## Acknowledgments

- [AbraFlexi](https://www.abraflexi.eu/) for the accounting platform
- [Model Context Protocol](https://modelcontextprotocol.io/) for the integration standard
- [FastMCP](https://github.com/jlowin/fastmcp) for the server framework

## Support

- 📖 [Documentation](README.md)
- 🐛 [Issue Tracker](https://github.com/VitexSoftware/abraflexi-mcp-server/issues)
- 💬 [AbraFlexi API Documentation](https://www.abraflexi.eu/api/dokumentace/)

## Author

**Vítězslav Dvořák**
- Email: info@vitexsoftware.cz
- GitHub: [@VitexSoftware](https://github.com/VitexSoftware)

---

**Made with ❤️ for the AbraFlexi and MCP communities**
