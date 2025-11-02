# 🧪 Quick Testing Guide - Multi-Server Setup

## Server Status Check

### Check All Running Servers
```bash
docker compose -f docker-compose.multi.yml ps
```

### Individual Health Checks
```bash
# Core Operations (Port 8001)
curl http://localhost:8001/health | jq

# Inventory Management (Port 8002)
curl http://localhost:8002/health | jq

# Templates (Port 8003)
curl http://localhost:8003/health | jq
```

### Get Server Info (includes tool list)
```bash
curl http://localhost:8001/ | jq
curl http://localhost:8002/ | jq
curl http://localhost:8003/ | jq
```

---

## API Documentation

Access interactive API docs (Swagger UI):
- Core: http://localhost:8001/docs
- Inventory: http://localhost:8002/docs
- Templates: http://localhost:8003/docs

---

## Testing Core Operations Server (8001)

### 1. List Job Templates
```bash
curl http://localhost:8001/job_templates | jq
```

### 2. Get Specific Job
```bash
curl http://localhost:8001/jobs/123 | jq
```

### 3. List Jobs (with pagination)
```bash
curl http://localhost:8001/jobs?page=1 | jq
```

### 4. Launch Job Template
```bash
curl -X POST http://localhost:8001/job_templates/10/launch \
  -H "Content-Type: application/json" \
  -d '{"extra_vars": {"key": "value"}}' | jq
```

### 5. Test AWX Connection
```bash
curl http://localhost:8001/test | jq
```

---

## Testing Inventory Management Server (8002)

### 1. List Inventories
```bash
curl http://localhost:8002/inventories | jq
```

### 2. Get Specific Inventory
```bash
curl http://localhost:8002/inventories/1 | jq
```

### 3. Create Inventory
```bash
curl -X POST http://localhost:8002/inventories \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Inventory",
    "organization": 1,
    "variables": {"env": "test"}
  }' | jq
```

### 4. List Hosts (all)
```bash
curl http://localhost:8002/hosts | jq
```

### 5. List Hosts (filtered by inventory)
```bash
curl http://localhost:8002/hosts?inventory=1 | jq
```

### 6. Create Host
```bash
curl -X POST http://localhost:8002/hosts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-host-01",
    "inventory": 1,
    "variables": {"ansible_host": "192.168.1.100"}
  }' | jq
```

### 7. Sync Inventory
```bash
curl -X POST http://localhost:8002/inventories/1/sync | jq
```

### 8. Delete Inventory (use with caution!)
```bash
curl -X DELETE http://localhost:8002/inventories/999 | jq
```

---

## Testing Templates Server (8003)

### 1. List Workflow Templates
```bash
curl http://localhost:8003/workflow_job_templates | jq
```

### 2. Create Job Template
```bash
curl -X POST http://localhost:8003/job_templates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Job Template",
    "inventory": 1,
    "project": 1,
    "playbook": "site.yml",
    "description": "Test playbook"
  }' | jq
```

### 3. Create Workflow Template
```bash
curl -X POST http://localhost:8003/workflow_job_templates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Workflow",
    "description": "Test workflow template"
  }' | jq
```

### 4. Update Workflow Template
```bash
curl -X PATCH http://localhost:8003/workflow_job_templates/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Workflow Name",
    "description": "Updated description"
  }' | jq
```

### 5. Launch Workflow Template
```bash
curl -X POST http://localhost:8003/workflow_job_templates/1/launch \
  -H "Content-Type: application/json" \
  -d '{"extra_vars": {"environment": "production"}}' | jq
```

### 6. Delete Workflow Template (use with caution!)
```bash
curl -X DELETE http://localhost:8003/workflow_job_templates/999 | jq
```

---

## Log Viewing

### View Logs for Each Server
```bash
# Core Operations
docker compose -f docker-compose.multi.yml logs core

# Inventory Management
docker compose -f docker-compose.multi.yml logs inventory

# Templates
docker compose -f docker-compose.multi.yml logs templates

# All servers
docker compose -f docker-compose.multi.yml logs -f
```

### Check Audit Logs
```bash
# Core logs
cat logs/core/mcp_server.log | tail -50

# Inventory logs
cat logs/inventory/mcp_server.log | tail -50

# Templates logs
cat logs/templates/mcp_server.log | tail -50
```

---

## Container Management

### Start All Servers
```bash
docker compose -f docker-compose.multi.yml up -d
```

### Start Specific Server
```bash
docker compose -f docker-compose.multi.yml up -d core
docker compose -f docker-compose.multi.yml up -d inventory
docker compose -f docker-compose.multi.yml up -d templates
```

### Stop All Servers
```bash
docker compose -f docker-compose.multi.yml down
```

### Restart Specific Server
```bash
docker compose -f docker-compose.multi.yml restart core
docker compose -f docker-compose.multi.yml restart inventory
docker compose -f docker-compose.multi.yml restart templates
```

### Rebuild and Restart
```bash
# Rebuild all
docker compose -f docker-compose.multi.yml build

# Rebuild specific
docker compose -f docker-compose.multi.yml build core
docker compose -f docker-compose.multi.yml build inventory
docker compose -f docker-compose.multi.yml build templates

# Rebuild and restart
docker compose -f docker-compose.multi.yml up -d --build
```

---

## Troubleshooting

### Check Server Status
```bash
docker compose -f docker-compose.multi.yml ps
```

### Check Container Logs (last 100 lines)
```bash
docker compose -f docker-compose.multi.yml logs --tail=100 core
```

### Check Container Resource Usage
```bash
docker stats mcp-server-core-1 mcp-server-inventory-1 mcp-server-templates-1
```

### Exec Into Container
```bash
docker exec -it mcp-server-core-1 /bin/bash
docker exec -it mcp-server-inventory-1 /bin/bash
docker exec -it mcp-server-templates-1 /bin/bash
```

### Test Network Connectivity
```bash
# From host to server
curl -v http://localhost:8001/health

# From one container to another
docker exec mcp-server-core-1 curl http://inventory:8002/health
```

### Check Environment Variables
```bash
docker exec mcp-server-core-1 env | grep AWX
```

---

## Performance Testing

### Simple Load Test (using ab - Apache Bench)
```bash
# Install if needed
sudo apt-get install apache2-utils

# Test Core Operations
ab -n 1000 -c 10 http://localhost:8001/health

# Test Inventory
ab -n 1000 -c 10 http://localhost:8002/health

# Test Templates
ab -n 1000 -c 10 http://localhost:8003/health
```

### Response Time Test
```bash
# Test Core
time curl http://localhost:8001/job_templates > /dev/null

# Test Inventory
time curl http://localhost:8002/inventories > /dev/null

# Test Templates
time curl http://localhost:8003/workflow_job_templates > /dev/null
```

---

## Integration Testing

### Test Cross-Server Workflow
```bash
# 1. List inventories (Inventory server)
INVENTORY_ID=$(curl -s http://localhost:8002/inventories | jq -r '.results[0].id')

# 2. List projects (need Projects server - not yet implemented)
# PROJECT_ID=...

# 3. Create job template (Templates server)
# Uses inventory from step 1 and project from step 2

# 4. Launch job (Core server)
# Uses template from step 3
```

---

## Expected Responses

### Healthy Server
```json
{
  "status": "healthy",
  "server": "Core Operations",
  "version": "2.0.0"
}
```

### Ready Check (when AWX connected)
```json
{
  "ready": true,
  "server": "Core Operations",
  "awx_connected": true
}
```

### Ready Check (when AWX not connected)
```json
{
  "ready": false,
  "server": "Core Operations",
  "awx_connected": false,
  "error": "Connection refused..."
}
```

### Server Info
```json
{
  "server": "Core Operations",
  "version": "2.0.0",
  "description": "Essential job execution and monitoring",
  "tools": ["list_templates", "launch_job_template", ...],
  "docs": "/docs",
  "health": "/health",
  "ready": "/ready"
}
```

---

## Quick Command Reference

```bash
# Start all servers
docker compose -f docker-compose.multi.yml up -d

# Check status
docker compose -f docker-compose.multi.yml ps

# View logs
docker compose -f docker-compose.multi.yml logs -f

# Test health (all servers)
curl http://localhost:8001/health && \
curl http://localhost:8002/health && \
curl http://localhost:8003/health

# Stop all servers
docker compose -f docker-compose.multi.yml down

# Rebuild everything
docker compose -f docker-compose.multi.yml build --no-cache
docker compose -f docker-compose.multi.yml up -d
```

---

## Common Issues & Solutions

### Issue: Port already in use
**Solution**: 
```bash
# Find process using port
sudo lsof -i :8001

# Kill process
kill -9 <PID>

# Or change port in docker-compose.multi.yml
```

### Issue: AWX connection failed
**Solution**:
```bash
# Check AWX_BASE_URL is correct
docker exec mcp-server-core-1 env | grep AWX

# Test AWX connectivity from container
docker exec mcp-server-core-1 curl http://192.168.122.46:31366/api/v2/ping/
```

### Issue: Container keeps restarting
**Solution**:
```bash
# Check logs
docker compose -f docker-compose.multi.yml logs core

# Common causes:
# - Import errors (shared/ not mounted correctly)
# - Syntax errors in Python code
# - Missing dependencies
```

### Issue: Can't access API docs
**Solution**:
```bash
# Verify server is running
curl http://localhost:8001/health

# Check port mapping
docker compose -f docker-compose.multi.yml ps

# Try accessing from container
docker exec mcp-server-core-1 curl http://localhost:8001/docs
```

---

**Last Updated**: 2025-11-01
**Version**: 1.0
