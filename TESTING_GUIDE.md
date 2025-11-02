# 🧪 Complete Testing Guide

## Quick Start - 3 Ways to Test

### 1. Interactive Menu (Easiest)
```bash
cd /home/ghost/awx_advanced_tools/mcp-server
./test.sh
```

Choose from options:
1. Quick Status Check
2. List All Resources
3. Test Specific Server
4. Open API Documentation
5. View Server Logs
6. Performance Test
7. Run Full Test Suite

### 2. Manual Commands (Most Flexible)
```bash
# Health check all servers
curl localhost:8001/health | jq
curl localhost:8002/health | jq
curl localhost:8003/health | jq

# Test AWX connectivity
curl localhost:8001/test | jq
curl localhost:8002/test | jq
curl localhost:8003/test | jq

# List resources
curl localhost:8001/job_templates | jq
curl localhost:8002/inventories | jq
curl localhost:8002/hosts | jq
```

### 3. Automated Test Suite (Most Comprehensive)
```bash
cd /home/ghost/awx_advanced_tools/mcp-server
./run_tests.sh
```

Runs 18+ automated tests across all servers.

---

## API Documentation (Interactive Testing)

### Swagger UI (Recommended)
Open in your browser:
- **Core Operations**: http://localhost:8001/docs
- **Inventory Management**: http://localhost:8002/docs
- **Templates**: http://localhost:8003/docs

Features:
- Try out API endpoints directly
- See request/response schemas
- Get example values
- Copy curl commands

### ReDoc (Alternative)
- **Core Operations**: http://localhost:8001/redoc
- **Inventory Management**: http://localhost:8002/redoc
- **Templates**: http://localhost:8003/redoc

---

## Testing by Server

### Core Operations (Port 8001)

**Available Tools**: 6
1. list_templates
2. launch_job_template
3. get_job
4. list_jobs
5. health_check
6. test_connection

**Quick Tests**:
```bash
# Server info
curl localhost:8001/ | jq

# List job templates
curl localhost:8001/job_templates | jq

# Get specific job
curl localhost:8001/jobs/1 | jq

# Launch template
TEMPLATE_ID=$(curl -s localhost:8001/job_templates | jq -r '.results[0].id')
curl -X POST localhost:8001/job_templates/$TEMPLATE_ID/launch \
  -H "Content-Type: application/json" \
  -d '{"extra_vars": {"test": true}}' | jq
```

---

### Inventory Management (Port 8002)

**Available Tools**: 8
1. list_inventories
2. get_inventory
3. create_inventory
4. delete_inventory
5. sync_inventory
6. list_hosts
7. create_host
8. test_connection

**Quick Tests**:
```bash
# Server info
curl localhost:8002/ | jq

# List inventories
curl localhost:8002/inventories | jq

# Get specific inventory
INV_ID=$(curl -s localhost:8002/inventories | jq -r '.results[0].id')
curl localhost:8002/inventories/$INV_ID | jq

# List all hosts
curl localhost:8002/hosts | jq

# List hosts in specific inventory
curl "localhost:8002/hosts?inventory=$INV_ID" | jq
```

---

### Templates (Port 8003)

**Available Tools**: 7
1. create_job_template
2. list_workflow_templates
3. create_workflow_template
4. update_workflow_template
5. delete_workflow_template
6. launch_workflow_template
7. test_connection

**Quick Tests**:
```bash
# Server info
curl localhost:8003/ | jq

# List workflow templates
curl localhost:8003/workflow_job_templates | jq

# Create workflow (creates real resource!)
curl -X POST localhost:8003/workflow_job_templates \
  -H "Content-Type: application/json" \
  -d '{"name": "Test-Workflow", "description": "Testing"}' | jq
```

---

## Integration Testing

### Multi-Server Workflow
```bash
# 1. Get inventory from Inventory server
INV_ID=$(curl -s localhost:8002/inventories | jq -r '.results[0].id')
echo "Using Inventory: $INV_ID"

# 2. Get template from Core server
TEMPLATE_ID=$(curl -s localhost:8001/job_templates | jq -r '.results[0].id')
echo "Using Template: $TEMPLATE_ID"

# 3. Launch job using that template
curl -X POST localhost:8001/job_templates/$TEMPLATE_ID/launch \
  -H "Content-Type: application/json" \
  -d '{"extra_vars": {}}' | jq
```

---

## Performance Testing

### Response Time Test
```bash
# Test each server
for port in 8001 8002 8003; do
  echo "Testing port $port..."
  time curl -s localhost:$port/health > /dev/null
done
```

### Load Test (requires apache-bench)
```bash
# Install if needed
sudo apt-get install apache2-utils

# Test with 100 requests, 10 concurrent
ab -n 100 -c 10 http://localhost:8001/health
ab -n 100 -c 10 http://localhost:8002/health
ab -n 100 -c 10 http://localhost:8003/health
```

---

## Troubleshooting

### Server Not Responding?
```bash
# Check container status
docker compose -f docker-compose.multi.yml ps

# Check logs
docker compose -f docker-compose.multi.yml logs core --tail=50
docker compose -f docker-compose.multi.yml logs inventory --tail=50
docker compose -f docker-compose.multi.yml logs templates --tail=50

# Restart if needed
docker compose -f docker-compose.multi.yml restart core
```

### AWX Connection Failed?
```bash
# Check AWX is accessible
curl http://192.168.122.46:31366/api/v2/ping/

# Check container environment
docker exec mcp-server-core-1 env | grep AWX

# Verify credentials
cat .env | grep AWX
```

### Port Already in Use?
```bash
# Find what's using the port
sudo lsof -i :8001

# Change port in docker-compose.multi.yml
# Then rebuild and restart
```

---

## Expected Results

### Healthy Server
```json
{
  "status": "healthy",
  "server": "Core Operations",
  "version": "2.0.0"
}
```

### Connected to AWX
```json
{
  "status": "connected",
  "template_count": 2
}
```

### Server Info
```json
{
  "server": "Core Operations",
  "version": "2.0.0",
  "description": "Essential job execution and monitoring",
  "tools": [
    "list_templates",
    "launch_job_template",
    "get_job",
    "list_jobs",
    "health_check",
    "test_connection"
  ],
  "docs": "/docs",
  "health": "/health",
  "ready": "/ready"
}
```

---

## Test Coverage

### What's Tested
✅ Container health and status  
✅ HTTP endpoint availability  
✅ AWX connectivity  
✅ Data retrieval from AWX  
✅ API documentation accessibility  
✅ Response times  
✅ Multi-server integration  

### What's NOT Tested (Yet)
⏳ Creating resources (requires careful cleanup)  
⏳ Deleting resources (dangerous in production)  
⏳ Error handling edge cases  
⏳ Authentication/authorization  
⏳ Rate limiting  
⏳ Concurrent requests  

---

## Quick Command Reference

```bash
# Start/Stop
docker compose -f docker-compose.multi.yml up -d
docker compose -f docker-compose.multi.yml down

# Status
docker compose -f docker-compose.multi.yml ps

# Logs
docker compose -f docker-compose.multi.yml logs -f

# Health check all
curl localhost:8001/health && curl localhost:8002/health && curl localhost:8003/health

# Test AWX all
curl localhost:8001/test | jq && curl localhost:8002/test | jq && curl localhost:8003/test | jq

# Interactive test menu
./test.sh

# Full test suite
./run_tests.sh
```

---

## Additional Resources

- **Detailed Testing**: See TEST_NOW.md
- **Quick Reference**: See QUICK_REFERENCE.md
- **API Examples**: See QUICK_TEST_GUIDE.md
- **Architecture**: See THREE_SERVERS_SUCCESS.md

---

**Pro Tips**:
1. Always use `jq` for pretty JSON output
2. Save resource IDs in variables for multi-step operations
3. Use browser-based API docs for interactive testing
4. Check logs immediately if something fails
5. Test read operations before write operations

---

*Last Updated: 2025-11-01*
*Version: 1.0*
