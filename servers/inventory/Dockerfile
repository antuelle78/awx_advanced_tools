# Dockerfile for Inventory Management MCP Server

FROM python:3.11-slim

# Install build dependencies
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared library
COPY shared/ /app/shared/

# Copy server code
COPY servers/inventory/ /app/servers/inventory/

# Expose port
EXPOSE 8002

# Run server
CMD ["python", "-m", "uvicorn", "servers.inventory.main:app", "--host", "0.0.0.0", "--port", "8002"]
