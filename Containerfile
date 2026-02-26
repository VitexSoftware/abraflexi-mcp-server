FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Install dependencies first (cached layer)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Copy source and install the project itself
COPY abraflexi_mcp_server/ abraflexi_mcp_server/
COPY scripts/ scripts/
COPY README.md ./
RUN uv sync --frozen --no-dev

# --- runtime stage ---
FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH" \
    ABRAFLEXI_MCP_TRANSPORT=streamable-http \
    ABRAFLEXI_MCP_HOST=0.0.0.0 \
    ABRAFLEXI_MCP_PORT=8000 \
    READ_ONLY=true

EXPOSE 8000

ENTRYPOINT ["abraflexi-mcp"]
