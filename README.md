# AbraFlexi MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/abraflexi-mcp-server.svg)](https://badge.fury.io/py/abraflexi-mcp-server)

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
- Access to an AbraFlexi server with API enabled

### Option 1: Install from PyPI (Recommended)

```bash
pip install abraflexi-mcp-server
```

Then run the server:
```bash
abraflexi-mcp
```

### Option 2: Install from Source

1. **Clone the repository:**
   ```bash
   git clone https://github.com/VitexSoftware/abraflexi-mcp-server.git
   cd abraflexi-mcp-server
   ```

2. **Install with uv (recommended):**
   ```bash
   uv sync
   uv run python scripts/start_server.py
   ```
   
   Or with pip:
   ```bash
   pip install -e .
   abraflexi-mcp
   ```

## Cloud Deployment

A testing deployment is available at:

**🌐 https://abraflexi.fastmcp.app/mcp**

This cloud-hosted instance allows you to test and use the AbraFlexi MCP server without local installation. Configure your MCP client to connect to this endpoint with HTTP transport.

**Note:** This is a testing deployment. For production use, we recommend self-hosting using one of the installation methods above.

### Configuration

Create a `.env` file or set environment variables:
```bash
cp .env.example .env
# Edit .env with your AbraFlexi server details
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

## OCI Container

The server can be run as an OCI container (Docker/Podman) — no Python installation needed on the host.

### Building the image

```bash
podman build -t abraflexi-mcp-server -f Containerfile .
```

### Running the container

The image defaults to `streamable-http` transport on port **8000**.

**With individual environment variables:**
```bash
podman run --rm -p 8000:8000 \
  -e ABRAFLEXI_URL=https://demo.flexibee.eu:5434 \
  -e ABRAFLEXI_COMPANY=demo_de \
  -e ABRAFLEXI_LOGIN=winstrom \
  -e ABRAFLEXI_PASSWORD=winstrom \
  abraflexi-mcp-server
```

**With an env file:**
```bash
podman run --rm -p 8000:8000 --env-file .env abraflexi-mcp-server
```

### Container environment defaults

| Variable | Default |
|---|---|
| `ABRAFLEXI_MCP_TRANSPORT` | `streamable-http` |
| `ABRAFLEXI_MCP_HOST` | `0.0.0.0` |
| `ABRAFLEXI_MCP_PORT` | `8000` |
| `READ_ONLY` | `true` |

All other [configuration variables](#configuration) can be passed as environment variables.

## AppImage

A self-contained, single-file Linux executable — no Python, pip, or any other dependency required on the host.

### Building the AppImage

```bash
bash appimage/build-appimage.sh
```

The script downloads a portable CPython and `appimagetool` automatically. The resulting file is placed in `build/appimage/`:

```
build/appimage/AbraFlexi-MCP-Server-1.0.0-x86_64.AppImage
```

### Running the AppImage

The AppImage automatically loads a `.env` file from the current working directory if one is present.

**With a .env file (recommended):**
```bash
cp .env.example .env
# edit .env with your credentials
./AbraFlexi-MCP-Server-1.0.0-x86_64.AppImage
```

**With inline environment variables:**
```bash
ABRAFLEXI_URL=https://demo.flexibee.eu:5434 \
ABRAFLEXI_COMPANY=demo_de \
ABRAFLEXI_LOGIN=winstrom \
ABRAFLEXI_PASSWORD=winstrom \
./AbraFlexi-MCP-Server-1.0.0-x86_64.AppImage
```

## Development

### Project Structure

```
abraflexi-mcp-server/
├── abraflexi_mcp_server/
│   ├── __init__.py
│   └── server.py                  # Main server implementation
├── appimage/
│   ├── AppRun                     # AppImage entry point
│   ├── abraflexi-mcp-server.desktop
│   ├── abraflexi-mcp-server.svg
│   └── build-appimage.sh          # AppImage build script
├── debian/                        # Debian packaging
├── scripts/
│   ├── start_server.py            # Startup script with validation
│   └── test_server.py             # Test script
├── Containerfile                  # OCI container build
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

<!-- mcp-name: io.github.Vitexus/abraflexi -->
