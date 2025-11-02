# 🚀 Quick Reference Card - Multi-Server MCP

## Server Ports & Status
```
✅ Core Operations:        http://localhost:8001  (6 tools)
✅ Inventory Management:   http://localhost:8002  (8 tools)
✅ Templates:              http://localhost:8003  (7 tools)
⬜ User Management:        http://localhost:8004  (pending)
⬜ Project Management:     http://localhost:8005  (pending)
⬜ Organization:           http://localhost:8006  (pending)
⬜ Schedules:              http://localhost:8007  (pending)
⬜ Advanced Operations:    http://localhost:8008  (pending)
⬜ Notifications:          http://localhost:8009  (pending)
⬜ Infrastructure:         http://localhost:8010  (pending)
```

## Essential Commands

### Start/Stop
```bash
# Start all servers
docker compose -f docker-compose.multi.yml up -d

# Stop all servers  
docker compose -f docker-compose.multi.yml down

# Restart specific server
docker compose -f docker-compose.multi.yml restart core
```

### Health Checks
```bash
# Quick health check all
curl localhost:8001/health && curl localhost:8002/health && curl localhost:8003/health

# Detailed server info
curl localhost:8001/ | jq
```

### View Logs
```bash
# All servers
docker compose -f docker-compose.multi.yml logs -f

# Specific server
docker compose -f docker-compose.multi.yml logs core -f
```

### Status Check
```bash
docker compose -f docker-compose.multi.yml ps
```

## API Endpoints Summary

### Core Operations (8001)
- GET `/job_templates` - List job templates
- POST `/job_templates/{id}/launch` - Launch job
- GET `/jobs` - List jobs
- GET `/jobs/{id}` - Get job status

### Inventory (8002)
- GET `/inventories` - List inventories
- POST `/inventories` - Create inventory
- GET `/hosts` - List hosts
- POST `/hosts` - Create host
- POST `/inventories/{id}/sync` - Sync inventory

### Templates (8003)
- POST `/job_templates` - Create job template
- GET `/workflow_job_templates` - List workflows
- POST `/workflow_job_templates` - Create workflow
- PATCH `/workflow_job_templates/{id}` - Update workflow
- POST `/workflow_job_templates/{id}/launch` - Launch workflow

## Test Examples

### Test AWX Connection
```bash
curl localhost:8001/test | jq
# Expected: {"status": "connected", "template_count": 2}
```

### List Resources
```bash
# Job templates
curl localhost:8001/job_templates | jq '.results[] | {id, name}'

# Inventories
curl localhost:8002/inventories | jq '.results[] | {id, name}'

# Hosts
curl localhost:8002/hosts | jq '.results[] | {id, name, inventory}'
```

### Create Resources
```bash
# Create inventory
curl -X POST localhost:8002/inventories \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "organization": 1}' | jq

# Create host
curl -X POST localhost:8002/hosts \
  -H "Content-Type: application/json" \
  -d '{"name": "host01", "inventory": 1}' | jq
```

## Documentation Links
- Core API: http://localhost:8001/docs
- Inventory API: http://localhost:8002/docs
- Templates API: http://localhost:8003/docs

## File Locations
- **Shared Code**: `/home/ghost/awx_advanced_tools/mcp-server/shared/`
- **Server Code**: `/home/ghost/awx_advanced_tools/mcp-server/servers/{server}/`
- **Logs**: `/home/ghost/awx_advanced_tools/mcp-server/logs/{server}/`
- **Compose**: `/home/ghost/awx_advanced_tools/mcp-server/docker-compose.multi.yml`

## AWX Configuration
```bash
AWX_BASE_URL=http://192.168.122.46:31366
AWX_USERNAME=openwebui
AWX_PASSWORD=openwebui
```

## Troubleshooting

### Server not starting?
```bash
# Check logs
docker compose -f docker-compose.multi.yml logs core

# Rebuild
docker compose -f docker-compose.multi.yml build core
docker compose -f docker-compose.multi.yml up -d core
```

### AWX connection failed?
```bash
# Verify AWX is accessible
curl http://192.168.122.46:31366/api/v2/ping/

# Check env vars in container
docker exec mcp-server-core-1 env | grep AWX
```

### Port already in use?
```bash
# Find process
sudo lsof -i :8001

# Or change port in docker-compose.multi.yml
```

## Next Steps
1. Review QUICK_TEST_GUIDE.md for detailed testing
2. Review THREE_SERVERS_SUCCESS.md for architecture details
3. Review SESSION_SUMMARY.md for implementation recap
4. Begin implementing User Management server (8004)

---
Last Updated: 2025-11-01 21:45:00
