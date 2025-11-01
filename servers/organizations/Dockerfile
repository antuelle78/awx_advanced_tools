# Dockerfile for Organization Management MCP Server

FROM python:3.11-slim

RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ /app/shared/
COPY servers/organizations/ /app/servers/organizations/

EXPOSE 8006

CMD ["python", "-m", "uvicorn", "servers.organizations.main:app", "--host", "0.0.0.0", "--port", "8006"]
