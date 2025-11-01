# 🚀 Multi-Server Deployment Guide

Complete guide for deploying the AWX Advanced Tools multi-server architecture in development, staging, and production environments.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Docker Compose Deployment](#docker-compose-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Configuration](#configuration)
6. [Health Monitoring](#health-monitoring)
7. [Troubleshooting](#troubleshooting)
8. [Scaling & Performance](#scaling--performance)

---

## Overview

The multi-server architecture consists of **10 specialized microservices**, each handling a specific domain of AWX functionality:

```
┌─────────────────────────────────────────────────────┐
│         Multi-Server Architecture (10 Servers)       │
├──────────┬──────────┬──────────┬──────────┬─────────┤
│ Core     │ Inventory│ Templates│ Users    │ Projects│
│ (8001)   │ (8002)   │ (8003)   │ (8004)   │ (8005)  │
├──────────┼──────────┼──────────┼──────────┼─────────┤
│ Orgs     │ Schedules│ Advanced │ Notify   │ Infra   │
│ (8006)   │ (8007)   │ (8008)   │ (8009)   │ (8010)  │
└──────────┴──────────┴──────────┴──────────┴─────────┘
```

Each server:
- Exposes 5-8 focused tools
- Runs on a dedicated port (8001-8010)
- Shares a common AWX client library
- Has independent scaling capabilities
- Includes health checks and monitoring

---

## Prerequisites

### Required
- **Docker**: 20.10+ (for Docker Compose deployment)
- **Docker Compose**: 2.0+ 
- **Kubernetes**: 1.20+ (for K8s deployment)
- **kubectl**: Latest version (for K8s deployment)
- **AWX Instance**: Running and accessible
- **Network Access**: Servers must reach AWX API

### Recommended
- **Redis**: For shared caching (included in compose files)
- **Monitoring**: Prometheus/Grafana for metrics
- **Ingress Controller**: For Kubernetes external access
- **Storage**: Persistent volumes for audit logs

---

## Docker Compose Deployment

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/antuelle78/awx_advanced_tools.git
cd awx_advanced_tools/mcp-server

# 2. Configure environment
cp .env.example .env
# Edit .env with your AWX credentials

# 3. Start all services
docker compose -f docker-compose.multi.yml up -d

# 4. Verify deployment
docker compose -f docker-compose.multi.yml ps
```

### Configuration

Edit `.env` file with your AWX settings:

```bash
# AWX Configuration
AWX_BASE_URL=http://your-awx-server:80
AWX_USERNAME=admin
AWX_PASSWORD=your_secure_password

# Optional: LLM Configuration
LLM_PROVIDER=ollama
LLM_ENDPOINT=http://host.docker.internal:11434
LLM_MODEL=granite3.1-dense:8b

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
```

### Service Ports

| Service | Port | URL |
|---------|------|-----|
| Core | 8001 | http://localhost:8001 |
| Inventory | 8002 | http://localhost:8002 |
| Templates | 8003 | http://localhost:8003 |
| Users | 8004 | http://localhost:8004 |
| Projects | 8005 | http://localhost:8005 |
| Organizations | 8006 | http://localhost:8006 |
| Schedules | 8007 | http://localhost:8007 |
| Advanced | 8008 | http://localhost:8008 |
| Notifications | 8009 | http://localhost:8009 |
| Infrastructure | 8010 | http://localhost:8010 |
| Redis | 6379 | Internal only |

### Managing Services

```bash
# Start all services
docker compose -f docker-compose.multi.yml up -d

# Stop all services
docker compose -f docker-compose.multi.yml down

# View logs (all services)
docker compose -f docker-compose.multi.yml logs -f

# View logs (specific service)
docker compose -f docker-compose.multi.yml logs -f core

# Restart a specific service
docker compose -f docker-compose.multi.yml restart inventory

# Rebuild after code changes
docker compose -f docker-compose.multi.yml build core
docker compose -f docker-compose.multi.yml up -d core

# Scale a specific service (if needed)
docker compose -f docker-compose.multi.yml up -d --scale inventory=3
```

### Volume Mounts

Each server has persistent audit logs:

```yaml
volumes:
  - ./logs/core:/var/log/mcp        # Core server logs
  - ./logs/inventory:/var/log/mcp   # Inventory server logs
  # ... etc for all servers
```

Logs are written to `./logs/{server-name}/mcp_server.log`

---

## Kubernetes Deployment

### Quick Start

```bash
# 1. Apply ConfigMap (contains AWX credentials)
kubectl apply -f k8s/configmap.yaml

# 2. Deploy all 10 servers
kubectl apply -f k8s/multi-server-deployment.yaml

# 3. Verify deployment
kubectl get pods -l tier=mcp-server
kubectl get services | grep mcp-
```

### ConfigMap Configuration

Edit `k8s/configmap.yaml` with your settings:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: awx-advanced-tools-config
data:
  AWX_BASE_URL: "http://your-awx-server:80"
  AWX_USERNAME: "admin"
  AWX_PASSWORD: "your_password"
  AUDIT_LOG_DIR: "/var/log/mcp"
  REDIS_HOST: "redis"
  REDIS_PORT: "6379"
  LLM_MODEL: "gpt-4o"
  LLM_ENDPOINT: "http://llm-service:11434"
```

### Service Access

Services are exposed as ClusterIP by default. For external access:

#### Option 1: Port Forward (Development)
```bash
# Forward core server to localhost
kubectl port-forward svc/mcp-core 8001:8001

# Forward inventory server
kubectl port-forward svc/mcp-inventory 8002:8002

# Test
curl http://localhost:8001/health
```

#### Option 2: NodePort (Staging)
Edit service type in `k8s/multi-server-deployment.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mcp-core
spec:
  type: NodePort  # Changed from ClusterIP
  selector:
    app: mcp-core
  ports:
  - protocol: TCP
    port: 8001
    targetPort: 8000
    nodePort: 30001  # External port
```

#### Option 3: Ingress (Production)
Create ingress resource:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mcp-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: mcp.example.com
    http:
      paths:
      - path: /core
        pathType: Prefix
        backend:
          service:
            name: mcp-core
            port:
              number: 8001
      - path: /inventory
        pathType: Prefix
        backend:
          service:
            name: mcp-inventory
            port:
              number: 8002
      # ... add paths for all servers
```

### Managing Deployments

```bash
# View all MCP pods
kubectl get pods -l tier=mcp-server

# View logs from specific server
kubectl logs -l app=mcp-core -f

# Restart a deployment
kubectl rollout restart deployment/mcp-inventory

# Scale a deployment
kubectl scale deployment/mcp-templates --replicas=3

# Delete all MCP resources
kubectl delete -f k8s/multi-server-deployment.yaml
```

### Persistent Storage

For audit logs, create PersistentVolumeClaim:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: audit-logs-pvc
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
```

Mount in each deployment:

```yaml
volumes:
- name: audit-logs
  persistentVolumeClaim:
    claimName: audit-logs-pvc
```

---

## Configuration

### Environment Variables

All servers accept the following environment variables:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `AWX_BASE_URL` | AWX API base URL | Yes | - |
| `AWX_USERNAME` | AWX admin username | Yes* | - |
| `AWX_PASSWORD` | AWX admin password | Yes* | - |
| `AWX_TOKEN` | AWX API token | Yes* | - |
| `AUDIT_LOG_DIR` | Audit log directory | No | `/var/log/mcp` |
| `REDIS_HOST` | Redis server hostname | No | `redis` |
| `REDIS_PORT` | Redis server port | No | `6379` |
| `LLM_PROVIDER` | LLM provider (`ollama`/`default`) | No | `default` |
| `LLM_ENDPOINT` | LLM API endpoint | No | - |
| `LLM_MODEL` | LLM model name | No | `gpt-4o` |
| `LLM_API_KEY` | LLM API key | No | - |

*Either `AWX_TOKEN` or `AWX_USERNAME`+`AWX_PASSWORD` required

### AWX Permissions

The AWX user/token must have the following permissions:
- Read access to inventories, templates, projects, users, organizations
- Execute permission on job templates
- Create/update/delete permissions for resources (based on use case)

Recommended: Create a dedicated AWX user with appropriate role assignments.

---

## Health Monitoring

### Health Check Endpoints

Each server exposes `/health` endpoint:

```bash
# Check all servers
for port in {8001..8010}; do
  echo -n "Port $port: "
  curl -s http://localhost:$port/health | jq -r '.status'
done
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-01T22:00:00Z"
}
```

### Docker Compose Health Checks

Health checks are configured in `docker-compose.multi.yml`:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 10s
```

View health status:
```bash
docker compose -f docker-compose.multi.yml ps
```

### Kubernetes Health Checks

Configured as liveness and readiness probes:

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 30
  timeoutSeconds: 10

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
  timeoutSeconds: 5
```

Check probe status:
```bash
kubectl describe pod <pod-name>
```

### Monitoring Stack (Optional)

Deploy Prometheus and Grafana:

```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus + Grafana
helm install monitoring prometheus-community/kube-prometheus-stack

# Access Grafana
kubectl port-forward svc/monitoring-grafana 3000:80
# Visit http://localhost:3000 (admin/prom-operator)
```

---

## Troubleshooting

### Common Issues

#### 1. Server Won't Start

**Symptoms**: Container exits immediately  
**Check**:
```bash
# View logs
docker logs mcp-server-core-1

# Common causes:
# - Missing AWX credentials
# - AWX server unreachable
# - Port already in use
```

**Fix**:
```bash
# Verify AWX connectivity
curl http://your-awx-server/api/v2/ping

# Check port usage
netstat -tuln | grep 8001

# Review environment variables
docker compose -f docker-compose.multi.yml config
```

#### 2. Health Check Failing

**Symptoms**: Health check returns unhealthy  
**Check**:
```bash
# Test health endpoint directly
curl -v http://localhost:8001/health

# Check container logs
docker logs mcp-server-core-1 --tail 50
```

**Fix**:
- Ensure AWX is reachable from container
- Check firewall rules
- Verify credentials are correct
- Increase health check timeout

#### 3. Cannot Connect to AWX

**Symptoms**: 500 errors, connection refused  
**Check**:
```bash
# Test from inside container
docker exec mcp-server-core-1 curl http://your-awx-server/api/v2/ping

# Check DNS resolution
docker exec mcp-server-core-1 nslookup your-awx-server
```

**Fix**:
```bash
# For host.docker.internal (Mac/Windows):
AWX_BASE_URL=http://host.docker.internal:11434

# For Linux, use host IP:
AWX_BASE_URL=http://192.168.1.100:80

# Or add to docker-compose.yml:
extra_hosts:
  - "awx-server:192.168.1.100"
```

#### 4. Shared Library Import Errors

**Symptoms**: `ModuleNotFoundError: No module named 'shared'`  
**Check**:
```bash
# Verify volume mount
docker inspect mcp-server-core-1 | grep -A 5 Mounts
```

**Fix**:
Ensure `docker-compose.multi.yml` has:
```yaml
volumes:
  - ./shared:/app/shared
```

#### 5. Out of Memory

**Symptoms**: Container killed, OOMKilled status  
**Check**:
```bash
docker stats
kubectl top pods
```

**Fix**:
Add memory limits:
```yaml
# docker-compose.yml
services:
  core:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

---

## Scaling & Performance

### Horizontal Scaling

#### Docker Compose
```bash
# Scale a specific service to 3 replicas
docker compose -f docker-compose.multi.yml up -d --scale inventory=3

# Requires load balancer in front
```

#### Kubernetes
```bash
# Scale deployment
kubectl scale deployment/mcp-inventory --replicas=3

# Auto-scale based on CPU
kubectl autoscale deployment mcp-inventory --cpu-percent=70 --min=2 --max=10
```

### Performance Tuning

#### 1. Redis Caching
Enable Redis for LLM response caching:

```python
# In config
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
```

#### 2. Connection Pooling
AWX client uses httpx connection pooling by default:

```python
# Adjust in shared/awx_client.py
self.client = httpx.AsyncClient(
    timeout=30.0,
    limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
)
```

#### 3. Resource Limits

Set appropriate limits per server:

```yaml
# Kubernetes
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

#### 4. Load Balancing

For high-traffic services, add multiple replicas behind a load balancer:

```yaml
# nginx.conf
upstream inventory-backend {
    server inventory-1:8002;
    server inventory-2:8002;
    server inventory-3:8002;
}

server {
    location /inventory {
        proxy_pass http://inventory-backend;
    }
}
```

### Monitoring Metrics

Key metrics to monitor:
- **Request rate**: Requests/second per server
- **Response time**: P50, P95, P99 latency
- **Error rate**: 4xx/5xx errors
- **CPU usage**: Per container
- **Memory usage**: Per container
- **AWX API latency**: External dependency health

---

## Security Considerations

### 1. Secrets Management

**Never commit credentials to git!**

#### Docker Compose
Use `.env` file (gitignored):
```bash
# .env
AWX_PASSWORD=super_secret_password
```

#### Kubernetes
Use Secrets:
```bash
# Create secret
kubectl create secret generic awx-credentials \
  --from-literal=username=admin \
  --from-literal=password=super_secret_password

# Reference in deployment
env:
- name: AWX_USERNAME
  valueFrom:
    secretKeyRef:
      name: awx-credentials
      key: username
```

### 2. Network Security

- Use TLS for AWX communication
- Restrict inter-service communication
- Implement network policies (Kubernetes)
- Use service mesh for mTLS (Istio/Linkerd)

### 3. Audit Logging

All operations are logged to audit logs:
```bash
# View audit logs
tail -f logs/core/mcp_server.log
```

---

## Next Steps

1. **Deploy to staging**: Test with real workloads
2. **Configure monitoring**: Set up Prometheus/Grafana
3. **Implement CI/CD**: Automate deployments
4. **Load testing**: Validate performance
5. **Security hardening**: Review and implement security best practices

---

## Support

- **Issues**: https://github.com/antuelle78/awx_advanced_tools/issues
- **Discussions**: https://github.com/antuelle78/awx_advanced_tools/discussions
- **Documentation**: See README.md and other docs in `/docs`

---

*Last Updated: November 1, 2025*  
*Version: 2.0.0*
