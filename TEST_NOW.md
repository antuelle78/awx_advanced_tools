# 🧪 Testing Guide - Current Multi-Server Setup

## Quick Status Check

### 1. Check All Containers
```bash
cd /home/ghost/awx_advanced_tools/mcp-server
docker compose -f docker-compose.multi.yml ps
```

### 2. Quick Health Check (All Servers)
```bash
echo "=== Health Checks ===" && \
curl -s http://localhost:8001/health | jq && \
curl -s http://localhost:8002/health | jq && \
curl -s http://localhost:8003/health | jq
```

### 3. AWX Connectivity Test
```bash
echo "=== AWX Connectivity ===" && \
curl -s http://localhost:8001/test | jq && \
curl -s http://localhost:8002/test | jq && \
curl -s http://localhost:8003/test | jq
```

---

## Core Operations Server (8001) Tests

### List Job Templates
```bash
curl -s http://localhost:8001/job_templates | jq '.results[] | {id, name, description}'
```

### Get Specific Job Template (replace 7 with actual ID)
```bash
curl -s http://localhost:8001/job_templates | jq '.results[0].id'
TEMPLATE_ID=$(curl -s http://localhost:8001/job_templates | jq -r '.results[0].id')
curl -s "http://localhost:8001/job_templates" | jq ".results[] | select(.id==$TEMPLATE_ID)"
```

### List Jobs
```bash
curl -s http://localhost:8001/jobs?page=1 | jq '{count: .count, jobs: [.results[] | {id, name, status}] | .[0:5]}'
```

### Launch Job (with extra vars)
```bash
# Get first template ID
TEMPLATE_ID=$(curl -s http://localhost:8001/job_templates | jq -r '.results[0].id')

# Launch it (dry run - won't actually execute)
curl -X POST http://localhost:8001/job_templates/$TEMPLATE_ID/launch \
  -H "Content-Type: application/json" \
  -d '{"extra_vars": {"test_mode": true}}' | jq
```

---

## Inventory Management Server (8002) Tests

### List All Inventories
```bash
curl -s http://localhost:8002/inventories | jq '{count: .count, inventories: [.results[] | {id, name, description}]}'
```

### Get Specific Inventory
```bash
INV_ID=$(curl -s http://localhost:8002/inventories | jq -r '.results[0].id')
curl -s http://localhost:8002/inventories/$INV_ID | jq '{id, name, description, organization}'
```

### List All Hosts
```bash
curl -s http://localhost:8002/hosts | jq '{count: .count, hosts: [.results[] | {id, name, inventory}] | .[0:10]}'
```

### List Hosts in Specific Inventory
```bash
INV_ID=$(curl -s http://localhost:8002/inventories | jq -r '.results[0].id')
curl -s "http://localhost:8002/hosts?inventory=$INV_ID" | jq '.results[] | {id, name, inventory}'
```

### Create Test Inventory (will create real resource!)
```bash
# WARNING: This creates a real inventory in AWX
curl -X POST http://localhost:8002/inventories \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test-Inventory-'$(date +%s)'",
    "description": "Created via MCP API test",
    "variables": {"test": true}
  }' | jq

# To clean up, get the ID and delete:
# TEST_INV_ID=$(curl -s http://localhost:8002/inventories | jq -r '.results[] | select(.name | startswith("Test-Inventory")) | .id')
# curl -X DELETE http://localhost:8002/inventories/$TEST_INV_ID | jq
```

### Create Test Host (will create real resource!)
```bash
# Get first inventory ID
INV_ID=$(curl -s http://localhost:8002/inventories | jq -r '.results[0].id')

# Create host
curl -X POST http://localhost:8002/hosts \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"test-host-$(date +%s)\",
    \"inventory\": $INV_ID,
    \"variables\": {\"ansible_host\": \"192.168.1.100\", \"test\": true}
  }" | jq
```

### Sync Inventory
```bash
INV_ID=$(curl -s http://localhost:8002/inventories | jq -r '.results[0].id')
curl -X POST http://localhost:8002/inventories/$INV_ID/sync | jq
```

---

## Templates Server (8003) Tests

### List Workflow Templates
```bash
curl -s http://localhost:8003/workflow_job_templates | jq '{count: .count, workflows: .results}'
```

### Create Job Template (will create real resource!)
```bash
# You need valid inventory ID and project ID
INV_ID=$(curl -s http://localhost:8002/inventories | jq -r '.results[0].id')

# Note: You need a valid project ID too - this might fail if no projects exist
curl -X POST http://localhost:8003/job_templates \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Test-Job-Template-$(date +%s)\",
    \"inventory\": $INV_ID,
    \"project\": 1,
    \"playbook\": \"test.yml\",
    \"description\": \"Created via MCP API test\"
  }" | jq
```

### Create Workflow Template (will create real resource!)
```bash
curl -X POST http://localhost:8003/workflow_job_templates \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Test-Workflow-$(date +%s)\",
    \"description\": \"Created via MCP API test\"
  }" | jq
```

### Update Workflow Template
```bash
# Get first workflow ID (if any exist)
WORKFLOW_ID=$(curl -s http://localhost:8003/workflow_job_templates | jq -r '.results[0].id // empty')

if [ -n "$WORKFLOW_ID" ]; then
  curl -X PATCH http://localhost:8003/workflow_job_templates/$WORKFLOW_ID \
    -H "Content-Type: application/json" \
    -d '{
      "description": "Updated via MCP API test"
    }' | jq
else
  echo "No workflows found to update"
fi
```

---

## API Documentation (Interactive)

### Swagger UI (Browser)
Open these URLs in your browser:
- Core Operations: http://localhost:8001/docs
- Inventory Management: http://localhost:8002/docs
- Templates: http://localhost:8003/docs

### ReDoc (Alternative Documentation)
- Core Operations: http://localhost:8001/redoc
- Inventory Management: http://localhost:8002/redoc
- Templates: http://localhost:8003/redoc

---

## Integration Testing

### Complete Workflow Test
```bash
echo "=== Integration Test: Create Full Stack ==="

# 1. Create organization (via future server - not yet implemented)
echo "Step 1: Organization - Skipped (server 8006 not yet deployed)"

# 2. Create inventory
echo -e "\nStep 2: Create Inventory"
INV_RESPONSE=$(curl -s -X POST http://localhost:8002/inventories \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Integration-Test-Inv-$(date +%s)\",
    \"description\": \"Integration test inventory\"
  }")
echo "$INV_RESPONSE" | jq
INV_ID=$(echo "$INV_RESPONSE" | jq -r '.id')

# 3. Create host in inventory
echo -e "\nStep 3: Create Host"
HOST_RESPONSE=$(curl -s -X POST http://localhost:8002/hosts \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"integration-host-$(date +%s)\",
    \"inventory\": $INV_ID,
    \"variables\": {\"ansible_host\": \"192.168.1.200\"}
  }")
echo "$HOST_RESPONSE" | jq
HOST_ID=$(echo "$HOST_RESPONSE" | jq -r '.id')

# 4. List job templates (from Core server)
echo -e "\nStep 4: List Available Job Templates"
curl -s http://localhost:8001/job_templates | jq '.results[] | {id, name}'

echo -e "\n=== Integration Test Complete ==="
echo "Created: Inventory ID=$INV_ID, Host ID=$HOST_ID"
```

---

## Performance Testing

### Simple Load Test (requires apache2-utils)
```bash
# Install if needed
# sudo apt-get install apache2-utils

# Test Core Operations
echo "Testing Core Operations..."
ab -n 100 -c 5 http://localhost:8001/health

# Test Inventory Management
echo "Testing Inventory Management..."
ab -n 100 -c 5 http://localhost:8002/health

# Test Templates
echo "Testing Templates..."
ab -n 100 -c 5 http://localhost:8003/health
```

### Response Time Test
```bash
echo "=== Response Time Tests ==="

echo "Core Operations:"
time curl -s http://localhost:8001/job_templates > /dev/null

echo "Inventory Management:"
time curl -s http://localhost:8002/inventories > /dev/null

echo "Templates:"
time curl -s http://localhost:8003/workflow_job_templates > /dev/null
```

---

## Troubleshooting Tests

### Check Container Logs
```bash
# All servers
docker compose -f docker-compose.multi.yml logs --tail=50

# Specific server
docker compose -f docker-compose.multi.yml logs --tail=50 core
docker compose -f docker-compose.multi.yml logs --tail=50 inventory
docker compose -f docker-compose.multi.yml logs --tail=50 templates
```

### Check Container Resources
```bash
docker stats mcp-server-core-1 mcp-server-inventory-1 mcp-server-templates-1 --no-stream
```

### Test Network Connectivity
```bash
# From host to containers
for port in 8001 8002 8003; do
  echo "Testing port $port..."
  nc -zv localhost $port
done

# From container to container
docker exec mcp-server-core-1 curl -s http://inventory:8002/health | jq
docker exec mcp-server-inventory-1 curl -s http://templates:8003/health | jq
```

### Check Environment Variables
```bash
docker exec mcp-server-core-1 env | grep AWX
docker exec mcp-server-inventory-1 env | grep AWX
docker exec mcp-server-templates-1 env | grep AWX
```

---

## Cleanup (Optional)

### Remove Test Resources from AWX
```bash
# List test inventories
curl -s http://localhost:8002/inventories | jq '.results[] | select(.name | contains("Test")) | {id, name}'

# Delete test inventory (replace ID)
# curl -X DELETE http://localhost:8002/inventories/<ID> | jq

# List test hosts
curl -s http://localhost:8002/hosts | jq '.results[] | select(.name | contains("test")) | {id, name}'

# Delete test host (replace ID)
# curl -X DELETE http://localhost:8002/hosts/<ID> | jq
```

---

## Expected Results

### Healthy System
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

### Successful Resource Creation
```json
{
  "id": 123,
  "name": "Test-Inventory-1234567890",
  "description": "Created via MCP API test",
  ...
}
```

---

## Quick Command Summary

```bash
# Start all servers
docker compose -f docker-compose.multi.yml up -d

# Health check all
curl localhost:8001/health && curl localhost:8002/health && curl localhost:8003/health

# AWX test all
curl localhost:8001/test | jq && curl localhost:8002/test | jq && curl localhost:8003/test | jq

# View logs
docker compose -f docker-compose.multi.yml logs -f

# Stop all
docker compose -f docker-compose.multi.yml down
```

---

**Pro Tips**:
1. Use `jq` for pretty JSON output
2. Save response IDs in variables for multi-step tests
3. Use `curl -v` for verbose output when debugging
4. Check logs immediately if something fails
5. Test with real AWX data before creating resources

---

*Last Updated: 2025-11-01*
