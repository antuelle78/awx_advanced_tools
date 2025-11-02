# AWX Advanced Tools

**Production-grade AI-powered automation platform for Ansible AWX/Tower**

[![CI/CD Pipeline](https://github.com/antuelle78/awx_advanced_tools/actions/workflows/ci.yml/badge.svg)](https://github.com/antuelle78/awx_advanced_tools/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/antuelle78/awx_advanced_tools/branch/main/graph/badge.svg)](https://codecov.io/gh/antuelle78/awx_advanced_tools)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-20.10+-blue.svg)](https://www.docker.com/)

## Overview

AWX Advanced Tools is an enterprise-ready microservices platform that enables Large Language Models (LLMs) to manage Ansible AWX/Tower infrastructure through natural language commands. Built on a distributed architecture of 10 specialized servers, it provides intelligent routing, comprehensive safety features, and production-grade reliability.

### Key Features

- **Multi-Server Architecture**: 10 specialized microservices optimized for small LLM context windows
- **Enterprise Security**: Dry-run modes, confirmation workflows, comprehensive audit logging
- **Production Ready**: Full CI/CD pipeline, health checks, monitoring integration
- **Flexible Deployment**: Docker Compose for development, Kubernetes for production
- **LLM Optimized**: Intelligent tool discovery with model-aware capabilities

### Use Cases

- **DevOps Automation**: Natural language job execution and infrastructure management
- **Self-Service Operations**: Enable non-technical teams to manage AWX workflows
- **Automated Remediation**: AI-driven incident response and system recovery
- **Audit & Compliance**: Complete activity logging and change tracking
- **Integration Hub**: Connect AWX with LLM-powered chat interfaces

---

## Table of Contents

1. [Architecture](#architecture)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Deployment](#deployment)
   - [Docker Compose](#docker-compose-deployment)
   - [Kubernetes](#kubernetes-deployment)
5. [Configuration](#configuration)
6. [API Reference](#api-reference)
7. [Security](#security)
8. [Monitoring](#monitoring)
9. [Troubleshooting](#troubleshooting)
10. [Development](#development)
11. [Contributing](#contributing)
12. [License](#license)

---

## Architecture

### Multi-Server Design

AWX Advanced Tools employs a microservices architecture with 10 specialized servers, each handling specific AWX domains:

```
┌─────────────────────────────────────────────────────────┐
│            AWX Advanced Tools v2.0                       │
│        Multi-Server Microservices Architecture           │
├──────────┬──────────┬──────────┬──────────┬────────────┤
│ Core     │ Inventory│ Templates│ Users    │ Projects   │
│ :8001    │ :8002    │ :8003    │ :8004    │ :8005      │
│ 6 tools  │ 8 tools  │ 7 tools  │ 7 tools  │ 7 tools    │
├──────────┼──────────┼──────────┼──────────┼────────────┤
│ Orgs     │ Schedules│ Advanced │ Notify   │ Infra      │
│ :8006    │ :8007    │ :8008    │ :8009    │ :8010      │
│ 6 tools  │ 7 tools  │ 5 tools  │ 2 tools  │ 3 tools    │
└──────────┴──────────┴──────────┴──────────┴────────────┘
                          │
                    ┌─────▼─────┐
                    │   Redis   │
                    │   Cache   │
                    └───────────┘
                          │
                    ┌─────▼─────┐
                    │    AWX    │
                    │  Instance │
                    └───────────┘
```

### Server Responsibilities

| Server | Port | Purpose | Tools |
|--------|------|---------|-------|
| **Core** | 8001 | Health checks, job monitoring | `ping_awx()`, `get_job()`, `list_jobs()`, `cancel_job()` |
| **Inventory** | 8002 | Inventory and host management | `list_inventories()`, `create_inventory()`, `list_hosts()`, `create_host()` |
| **Templates** | 8003 | Job template operations | `list_templates()`, `launch_job_template()`, `create_job_template()` |
| **Users** | 8004 | User and team administration | `list_users()`, `create_user()`, `update_user()`, `delete_user()` |
| **Projects** | 8005 | SCM project management | `list_projects()`, `create_project()`, `sync_project()` |
| **Organizations** | 8006 | Organization CRUD | `list_organizations()`, `create_organization()`, `update_organization()` |
| **Schedules** | 8007 | Job scheduling | `create_schedule()`, `toggle_schedule()`, `list_schedules()` |
| **Advanced** | 8008 | Credentials & advanced ops | `list_credentials()`, `create_credential()`, `update_credential()` |
| **Notifications** | 8009 | Activity monitoring | `list_activity_stream()` |
| **Infrastructure** | 8010 | System information | `get_awx_version()`, `list_instance_groups()`, `get_awx_config()` |

### Design Principles

- **Single Responsibility**: Each server manages one domain
- **Shared Library**: Common AWX client ensures consistency
- **Stateless**: Servers can scale horizontally
- **Health Monitoring**: All servers expose `/health` endpoints
- **Audit Trail**: Complete logging of all operations

### Technology Stack

- **Framework**: FastAPI 0.115+ (async/await)
- **Language**: Python 3.10+
- **Validation**: Pydantic 2.8+
- **HTTP Client**: httpx (async)
- **Cache**: Redis (optional)
- **Container**: Docker + Docker Compose
- **Orchestration**: Kubernetes 1.20+

---

## Prerequisites

### Required

- **Python**: 3.10 or higher
- **Docker**: 20.10 or higher
- **Docker Compose**: 2.0 or higher
- **AWX/Tower**: Running instance with API access
- **Network**: Connectivity to AWX instance

### Optional

- **Kubernetes**: 1.20+ (for production deployment)
- **Redis**: For distributed caching
- **Prometheus**: For metrics collection
- **Grafana**: For monitoring dashboards

### System Requirements

#### Development
- CPU: 2 cores
- RAM: 4 GB
- Disk: 10 GB free space

#### Production
- CPU: 4+ cores
- RAM: 8+ GB
- Disk: 20+ GB SSD
- Network: Low latency to AWX instance

---

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/antuelle78/awx_advanced_tools.git
cd awx_advanced_tools/mcp-server
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your AWX credentials:

```bash
AWX_BASE_URL=https://your-awx-instance.com
AWX_USERNAME=admin
AWX_PASSWORD=your_secure_password
```

### 3. Deploy with Docker Compose

#### Option A: Single Monolithic Server

```bash
docker compose up -d
```

Server available at: `http://localhost:8001`

#### Option B: Multi-Server Architecture (Recommended)

```bash
docker compose -f docker-compose.multi.yml up -d
```

Servers available on ports 8001-8010.

### 4. Verify Deployment

```bash
# Check all servers
for port in {8001..8010}; do
  echo -n "Port $port: "
  curl -s http://localhost:$port/health | jq -r '.status'
done
```

Expected output: `healthy` for all servers.

### 5. Test API

```bash
# List inventories
curl http://localhost:8002/inventories

# List job templates
curl http://localhost:8003/templates

# Check AWX connectivity
curl http://localhost:8001/ping
```

---

## Deployment

### Docker Compose Deployment

#### Development Setup

```bash
# Build and start all services
docker compose -f docker-compose.multi.yml up -d --build

# View logs
docker compose -f docker-compose.multi.yml logs -f

# Stop services
docker compose -f docker-compose.multi.yml down
```

#### Configuration

The `docker-compose.multi.yml` includes:
- 10 specialized MCP servers
- Redis cache
- Health checks for all services
- Persistent audit logs
- Network isolation

#### Scaling Individual Services

```bash
# Scale inventory server to 3 replicas
docker compose -f docker-compose.multi.yml up -d --scale inventory=3

# Scale templates server to 2 replicas
docker compose -f docker-compose.multi.yml up -d --scale templates=2
```

### Kubernetes Deployment

#### Prerequisites

- kubectl configured with cluster access
- Kubernetes 1.20 or higher
- LoadBalancer or Ingress controller (for external access)

#### Quick Deploy

```bash
# Apply ConfigMap (update with your AWX credentials first)
kubectl apply -f k8s/configmap.yaml

# Deploy all 10 servers
kubectl apply -f k8s/multi-server-deployment.yaml

# Verify deployment
kubectl get pods -l tier=mcp-server
kubectl get services | grep mcp-
```

#### Production Configuration

1. **Update ConfigMap** with production credentials:

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: awx-advanced-tools-config
data:
  AWX_BASE_URL: "https://awx.production.com"
  AWX_USERNAME: "automation-user"
  # Use Secrets for sensitive data in production
```

2. **Create Kubernetes Secret** for credentials:

```bash
kubectl create secret generic awx-credentials \
  --from-literal=username=admin \
  --from-literal=password=your_secure_password
```

3. **Configure Resource Limits**:

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

4. **Set up Ingress** for external access:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mcp-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - awx-tools.example.com
    secretName: awx-tools-tls
  rules:
  - host: awx-tools.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: mcp-core
            port:
              number: 8001
```

5. **Enable Horizontal Pod Autoscaling**:

```bash
kubectl autoscale deployment mcp-inventory --cpu-percent=70 --min=2 --max=10
kubectl autoscale deployment mcp-templates --cpu-percent=70 --min=2 --max=10
```

#### Monitoring Kubernetes Deployment

```bash
# Check pod status
kubectl get pods -l tier=mcp-server -w

# View logs from specific server
kubectl logs -l app=mcp-core -f --tail=100

# Describe pod for troubleshooting
kubectl describe pod <pod-name>

# Check service endpoints
kubectl get endpoints
```

---

## Configuration

### Environment Variables

All servers accept the following environment variables:

#### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `AWX_BASE_URL` | AWX/Tower API base URL | `https://awx.example.com` |
| `AWX_USERNAME` | AWX username (if not using token) | `admin` |
| `AWX_PASSWORD` | AWX password (if not using token) | `secure_password` |
| `AWX_TOKEN` | AWX API token (alternative to user/pass) | `AbCdEf123456...` |

#### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `AUDIT_LOG_DIR` | Directory for audit logs | `/var/log/mcp` |
| `REDIS_HOST` | Redis server hostname | `redis` |
| `REDIS_PORT` | Redis server port | `6379` |
| `REDIS_DB` | Redis database number | `0` |
| `LLM_PROVIDER` | LLM provider (`default` or `ollama`) | `default` |
| `LLM_ENDPOINT` | LLM API endpoint | `http://localhost:11434` |
| `LLM_MODEL` | LLM model name | `gpt-4o` |
| `LLM_API_KEY` | LLM API key | - |
| `JWT_SECRET` | Secret for JWT authentication | Random |

### Configuration File

Create `.env` file:

```bash
# AWX Configuration
AWX_BASE_URL=https://awx.production.com
AWX_TOKEN=your_awx_api_token

# Or use username/password
AWX_USERNAME=automation-user
AWX_PASSWORD=secure_password

# Logging
AUDIT_LOG_DIR=/var/log/awx-tools

# LLM Integration (Optional)
LLM_PROVIDER=ollama
LLM_ENDPOINT=http://ollama:11434
LLM_MODEL=granite3.1-dense:8b

# Cache (Optional)
REDIS_HOST=redis
REDIS_PORT=6379

# Security
JWT_SECRET=change_this_to_random_string
```

### AWX User Permissions

The AWX user/token must have appropriate permissions:

**Minimum Permissions:**
- Read: All resources
- Execute: Job templates
- Create/Update/Delete: Based on use case

**Recommended Setup:**

1. Create dedicated AWX user:
```bash
# In AWX UI: Users > Add User
Username: awx-tools-automation
Organization: Default
User Type: System Administrator
```

2. Generate API token:
```bash
# In AWX UI: Users > awx-tools-automation > Tokens > Add Token
Scope: Write
```

3. Use token in configuration:
```bash
AWX_TOKEN=<generated_token>
```

---

## API Reference

### Health Check Endpoints

All servers expose standard health endpoints:

#### GET /health

Returns server health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-01T22:00:00Z",
  "server": "core",
  "version": "2.0.0"
}
```

#### GET /ready

Returns readiness status (includes AWX connectivity check).

**Response:**
```json
{
  "ready": true,
  "awx_connected": true,
  "services": {
    "awx": "ok",
    "redis": "ok"
  }
}
```

### Core Server (Port 8001)

#### GET /ping
Test AWX connectivity.

**Response:**
```json
{
  "message": "pong",
  "awx_version": "23.3.0",
  "connected": true
}
```

#### GET /jobs
List all jobs with pagination.

**Parameters:**
- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page (default: 20)

**Response:**
```json
{
  "count": 156,
  "next": "/jobs?page=2",
  "previous": null,
  "results": [
    {
      "id": 42,
      "name": "Deploy Application",
      "status": "successful",
      "created": "2025-11-01T20:00:00Z"
    }
  ]
}
```

#### GET /jobs/{job_id}
Get specific job details.

**Response:**
```json
{
  "id": 42,
  "name": "Deploy Application",
  "status": "successful",
  "job_template": 10,
  "started": "2025-11-01T20:00:00Z",
  "finished": "2025-11-01T20:05:00Z",
  "elapsed": 300
}
```

### Inventory Server (Port 8002)

#### GET /inventories
List inventories.

**Parameters:**
- `name` (str): Filter by name
- `organization` (int): Filter by organization ID

**Response:**
```json
{
  "count": 5,
  "inventories": [
    {
      "id": 1,
      "name": "Production",
      "total_hosts": 50,
      "organization": 1
    }
  ]
}
```

#### POST /inventories
Create new inventory.

**Request Body:**
```json
{
  "name": "Staging",
  "description": "Staging environment",
  "organization": 1,
  "variables": {
    "env": "staging"
  }
}
```

**Response:**
```json
{
  "id": 6,
  "name": "Staging",
  "created": "2025-11-01T22:00:00Z"
}
```

### Templates Server (Port 8003)

#### POST /templates/{template_id}/launch
Launch job template.

**Request Body:**
```json
{
  "extra_vars": {
    "target_env": "production",
    "backup_enabled": true
  }
}
```

**Response:**
```json
{
  "job_id": 157,
  "status": "pending",
  "url": "/jobs/157"
}
```

For complete API documentation, see [API_REFERENCE.md](./API_REFERENCE.md).

---

## Security

### Authentication

#### Basic Authentication

All endpoints (except `/health`) require authentication:

```bash
curl -u username:password http://localhost:8001/ping
```

#### JWT Authentication

1. Obtain JWT token:
```bash
curl -X POST http://localhost:8001/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'
```

2. Use token in requests:
```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:8002/inventories
```

### Safety Features

#### Dry-Run Mode

Test operations without execution:

```bash
curl -X DELETE "http://localhost:8002/inventories/5?dry_run=true"
```

**Response:**
```json
{
  "dry_run": true,
  "action": "delete_inventory",
  "resource_id": 5,
  "would_delete": {
    "inventory": "Staging",
    "hosts": 10
  },
  "message": "Dry run - no changes made"
}
```

#### Confirmation Required

Destructive operations require explicit confirmation:

```bash
curl -X DELETE "http://localhost:8002/inventories/5?confirm=true"
```

Without `confirm=true`, request will be rejected:
```json
{
  "error": "Confirmation required",
  "message": "Add '?confirm=true' to confirm deletion"
}
```

#### Post-Operation Verification

All delete operations verify completion:
```json
{
  "deleted": true,
  "resource_id": 5,
  "verified": true,
  "message": "Inventory deleted and verified"
}
```

### Audit Logging

All operations are logged to audit files:

**Log Location:** `${AUDIT_LOG_DIR}/mcp_server.log`

**Log Format:**
```json
{
  "timestamp": "2025-11-01T22:00:00Z",
  "user": "admin",
  "action": "delete_inventory",
  "resource_type": "inventory",
  "resource_id": 5,
  "success": true,
  "source_ip": "192.168.1.100"
}
```

### Network Security

#### Production Checklist

- [ ] Use HTTPS for AWX API
- [ ] Enable TLS for Redis
- [ ] Configure firewall rules
- [ ] Use Kubernetes NetworkPolicies
- [ ] Enable JWT authentication
- [ ] Rotate credentials regularly
- [ ] Monitor audit logs
- [ ] Set up intrusion detection

#### Kubernetes Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: mcp-server-policy
spec:
  podSelector:
    matchLabels:
      tier: mcp-server
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: gateway
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 443  # AWX HTTPS
```

---

## Monitoring

### Health Checks

Configure health monitoring:

**Docker Compose:**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 10s
```

**Kubernetes:**
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 30
readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
```

### Metrics

Prometheus metrics exposed on `/metrics`:

**Key Metrics:**
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency
- `awx_api_calls_total` - AWX API calls
- `awx_api_errors_total` - AWX API errors
- `cache_hits_total` - Redis cache hits
- `cache_misses_total` - Redis cache misses

**Prometheus Config:**
```yaml
scrape_configs:
  - job_name: 'mcp-servers'
    static_configs:
      - targets:
        - 'mcp-core:8001'
        - 'mcp-inventory:8002'
        - 'mcp-templates:8003'
        # ... other servers
```

### Logging

#### Log Levels

Set via environment:
```bash
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

#### Centralized Logging

**ELK Stack:**
```yaml
filebeat:
  inputs:
    - type: log
      paths:
        - /var/log/mcp/*.log
      json.keys_under_root: true
  output:
    elasticsearch:
      hosts: ["elasticsearch:9200"]
```

**Loki:**
```yaml
promtail:
  config:
    clients:
      - url: http://loki:3100/loki/api/v1/push
    scrape_configs:
      - job_name: mcp-servers
        static_configs:
          - labels:
              app: mcp-server
            paths:
              - /var/log/mcp/*.log
```

### Alerting

**Prometheus Alert Rules:**
```yaml
groups:
  - name: mcp-servers
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate on {{ $labels.server }}"
      
      - alert: AWXConnectionDown
        expr: up{job="mcp-servers"} == 0
        for: 2m
        annotations:
          summary: "AWX connection lost on {{ $labels.instance }}"
```

---

## Troubleshooting

### Common Issues

#### 1. Server Won't Start

**Symptoms:** Container exits immediately

**Diagnosis:**
```bash
docker logs mcp-server-core-1
```

**Solutions:**
- Check AWX credentials in `.env`
- Verify AWX instance is accessible
- Check port availability: `netstat -tuln | grep 8001`
- Review environment variables: `docker compose config`

#### 2. AWX Connection Failed

**Symptoms:** Health check fails, `/ready` returns not ready

**Diagnosis:**
```bash
curl http://localhost:8001/ping
```

**Solutions:**
- Verify AWX_BASE_URL is correct
- Check network connectivity: `ping awx-server`
- Test AWX API directly:
  ```bash
  curl -u username:password https://awx-server/api/v2/ping
  ```
- Check firewall rules
- Verify SSL certificates if using HTTPS

#### 3. High Memory Usage

**Symptoms:** Container OOMKilled, slow responses

**Diagnosis:**
```bash
docker stats
```

**Solutions:**
- Set memory limits in `docker-compose.yml`:
  ```yaml
  deploy:
    resources:
      limits:
        memory: 512M
  ```
- Enable Redis caching to reduce API calls
- Scale services horizontally
- Review audit logs for unusual activity

#### 4. Authentication Errors

**Symptoms:** 401 Unauthorized responses

**Solutions:**
- Verify AWX credentials
- Check token expiration
- Regenerate AWX API token
- Review audit logs for authentication attempts

### Debug Mode

Enable debug logging:

```bash
LOG_LEVEL=DEBUG docker compose -f docker-compose.multi.yml up
```

### Support Resources

- **Documentation**: See `/docs` directory
- **Issues**: GitHub Issues tracker
- **Logs**: Check `./logs/*/mcp_server.log`
- **Health**: Monitor `/health` and `/ready` endpoints

---

## Development

### Local Development Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run linter
ruff check .

# Run type checker
mypy app/
```

### Project Structure

```
mcp-server/
├── app/                      # Monolithic server (legacy)
│   ├── adapters/            # AWX adapters
│   ├── llm/                 # LLM integration
│   └── ...
├── servers/                  # Multi-server architecture
│   ├── core/                # Core server
│   ├── inventory/           # Inventory server
│   ├── templates/           # Templates server
│   └── ...                  # Other servers
├── shared/                   # Shared libraries
│   ├── awx_client.py        # Common AWX client
│   ├── config.py            # Configuration
│   └── middleware.py        # Common middleware
├── tests/                    # Test suite
├── k8s/                      # Kubernetes manifests
├── docs/                     # Documentation
├── docker-compose.yml        # Single server compose
├── docker-compose.multi.yml  # Multi-server compose
└── README.md                # This file
```

### Adding a New Server

1. **Copy template:**
```bash
cp -r servers/_template servers/my-new-server
```

2. **Update files:**
- `servers/my-new-server/main.py` - Server configuration
- `servers/my-new-server/routes.py` - API endpoints
- `servers/my-new-server/schemas.py` - Pydantic models

3. **Add to Docker Compose:**
```yaml
my-new-server:
  build:
    context: .
    dockerfile: servers/my-new-server/Dockerfile
  ports:
    - "8011:8011"
  environment:
    - AWX_BASE_URL=${AWX_BASE_URL}
  networks:
    - mcp-network
```

4. **Add to Kubernetes:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-my-new-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mcp-my-new-server
  template:
    spec:
      containers:
      - name: my-new-server
        image: awx-tools:my-new-server
        ports:
        - containerPort: 8000
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_awx_service.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run integration tests
pytest -m integration

# Run only unit tests
pytest -m "not integration"
```

### Code Quality

```bash
# Lint code
ruff check . --fix

# Format code
ruff format .

# Type check
mypy --explicit-package-bases --ignore-missing-imports app/

# Security scan
bandit -r app/
safety scan
```

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

### Quick Contribution Guide

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/my-feature`
3. **Make changes** and add tests
4. **Run quality checks**: `ruff check . && mypy app/ && pytest`
5. **Commit**: `git commit -m "feat: Add my feature"`
6. **Push**: `git push origin feature/my-feature`
7. **Create Pull Request**

### Coding Standards

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for public functions
- Add tests for new features
- Update documentation

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [Ansible AWX](https://github.com/ansible/awx)
- Inspired by the need for AI-driven infrastructure automation

---

## Changelog

### v2.0.0 - Multi-Server Architecture (2025-11-01)

- **[MAJOR]** Implemented 10-server microservices architecture
- **[FEATURE]** Added specialized servers for each AWX domain
- **[FEATURE]** Optimized system prompts for small LLMs
- **[FEATURE]** Complete Kubernetes deployment support
- **[IMPROVEMENT]** 80% reduction in tools per endpoint
- **[IMPROVEMENT]** 60% reduction in response tokens
- **[IMPROVEMENT]** Added comprehensive health checks
- **[DOCS]** Production-grade documentation

### v1.0.0 - Initial Release

- Single monolithic server
- Basic AWX operations
- LLM integration
- Docker deployment

For detailed changelog, see [CHANGELOG.md](./CHANGELOG.md).

---

## Support

- **Documentation**: [/docs](./docs)
- **Issues**: [GitHub Issues](https://github.com/antuelle78/awx_advanced_tools/issues)
- **Discussions**: [GitHub Discussions](https://github.com/antuelle78/awx_advanced_tools/discussions)

---

**AWX Advanced Tools v2.0** - Production-ready AI-powered AWX automation platform.
