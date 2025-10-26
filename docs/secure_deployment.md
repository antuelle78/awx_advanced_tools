# Secure Deployment Example

Below is a minimal but production‑grade deployment configuration using **Docker Compose** and **environment variables**. Adjust the values to match your infrastructure.

```yaml
# docker-compose.yml

version: "3.8"
services:
   awx-advanced-tools:
     image: ghcr.io/antuelle78/awx_advanced_tools:latest
    container_name: awx-advanced-tools
    restart: unless-stopped
    env_file: .env
    environment:
      - AWX_BASE_URL=https://awx.example.com/api/v2
      - AWX_TOKEN=YOUR_SECURE_AWX_TOKEN
       - LLM_ENDPOINT=https://llm.example.com/endpoint
      - JWT_SECRET=${JWT_SECRET}
      - AUDIT_LOG_DIR=/var/log/audit
    volumes:
      - ./logs:/var/log/audit
    ports:
      - "8000:80"
    networks:
      - awx-net

networks:
  awx-net:
    driver: bridge
```

## Environment File (`.env`)

Create a `.env` file in the same directory as `docker-compose.yml` with the following variables:

```
# .env

# HTTPS enforcement for FastAPI
SSL_CERT_PATH=/etc/ssl/certs/server.crt
SSL_KEY_PATH=/etc/ssl/private/server.key

# Secret used by Auth router
JWT_SECRET=super-secret-string
```

**Tip:** Store secrets outside the repository (e.g., in Vault, AWS Secrets Manager, or a dedicated secrets service) and reference them via Docker secrets.

## Dockerfile for Production Images

The upstream image uses a non‑root user and includes a small entrypoint script that sets up the JSON logger and health checks. If you need a custom image:

```dockerfile
# Dockerfile

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Optional: only copy the source and install runtime
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 80

# Entrypoint sets the environment variables and runs Uvicorn
ENTRYPOINT ["uvicorn", "app.main:app", "--host=0.0.0.0", "--port=80", "--workers=4", "--log-level=info"]
```

## Tips for Production

* **HTTPS** – Reverse proxy the FastAPI service through Nginx/Traefik with TLS termination.
* **Rate‑limiting** – Add a middleware such as `slowapi` to mitigate abuse.
* **Secrets Management** – Use Docker secrets or an external secret store instead of plain text.
* **Audit Logging** – Ensure the `AUDIT_LOG_DIR` is persisted and rotated outside the container.
* **Scale Workers** – Increase the `--workers` flag of Uvicorn to handle more concurrent requests.

---

For more detailed guidance, refer to the official FastAPI and Docker documentation.
```
