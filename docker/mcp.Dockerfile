# MCP Service - Lightweight HTTP-based microservice  
FROM python:3.12-slim

WORKDIR /api

# Install uv
RUN pip install --no-cache-dir uv

# Copy pyproject.toml for dependency installation
COPY pyproject.toml .

# Install only mcp dependencies using uv
RUN uv pip install --system --group mcp

# Create minimal directory structure
RUN mkdir -p mcp_server/features/projects mcp_server/features/tasks mcp_server/features/documents src/server/services src/server/config

# Copy only MCP-specific files
COPY mcp_server/ mcp_server/
COPY src/__init__.py src/

# Copy the server files MCP needs for HTTP communication
COPY src/server/__init__.py src/server/
COPY src/server/services/__init__.py src/server/services/
COPY src/server/services/mcp_service_client.py src/server/services/
COPY src/server/services/client_manager.py src/server/services/
COPY src/server/services/mcp_session_manager.py src/server/services/
COPY src/server/config/__init__.py src/server/config/
COPY src/server/config/service_discovery.py src/server/config/
COPY src/server/config/logfire_config.py src/server/config/

# Set environment variables
ENV PYTHONPATH="/app:$PYTHONPATH"
ENV PYTHONUNBUFFERED=1

# Expose MCP port
ARG AIEXEC_MCP_PORT=8051
ENV AIEXEC_MCP_PORT=${AIEXEC_MCP_PORT}
EXPOSE ${AIEXEC_MCP_PORT}

# Run the MCP server
CMD ["python", "-m", "src.mcp_server.mcp_server"]
