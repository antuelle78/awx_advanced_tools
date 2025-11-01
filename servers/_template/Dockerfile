# Dockerfile for {SERVER_NAME} MCP Server

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
COPY servers/_template/ /app/servers/_template/

# Expose port
EXPOSE {PORT}

# Run server
CMD ["uvicorn", "servers._template.main:app", "--host", "0.0.0.0", "--port", "{PORT}"]
