# 📋 Detailed Refactoring Plan: Multi-MCP Server Architecture

## 🎯 Executive Summary

**Problem**: LLMs with `max_tools <= 10` are overwhelmed by the monolithic tool exposure, even with progressive tool grouping.

**Solution**: Refactor into **specialized MCP servers** - one per tool group - allowing clients to connect to specific servers based on their needs, reducing cognitive load and improving performance.

**Impact**:
- Better performance for small models (135M-3B parameters)
- Clearer separation of concerns
- Easier testing and maintenance
- More granular access control

---

## 🏗️ Proposed Architecture

### Current Architecture (Monolithic)
```
┌─────────────────────────────────┐
│     Single MCP Server           │
│  (All 40+ tools in one server)  │
│                                 │
│  • Basic (6 tools)              │
│  • Inventory (5 tools)          │
│  • Users (6 tools)              │
│  • Projects (6 tools)           │
│  • Organizations (5 tools)      │
│  • Schedules (5 tools)          │
│  • Advanced (19 tools)          │
└─────────────────────────────────┘
```

### Proposed Architecture (Microservices)
```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  MCP: Basic      │  │  MCP: Inventory  │  │  MCP: Templates  │
│  Port: 8001      │  │  Port: 8002      │  │  Port: 8003      │
│  (6 tools)       │  │  (5 tools)       │  │  (8 tools)       │
└──────────────────┘  └──────────────────┘  └──────────────────┘

┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  MCP: Users      │  │  MCP: Projects   │  │  MCP: Orgs       │
│  Port: 8004      │  │  Port: 8005      │  │  Port: 8006      │
│  (6 tools)       │  │  (6 tools)       │  │  (5 tools)       │
└──────────────────┘  └──────────────────┘  └──────────────────┘

┌──────────────────┐  ┌──────────────────┐
│  MCP: Schedules  │  │  MCP: Advanced   │
│  Port: 8007      │  │  Port: 8008      │
│  (5 tools)       │  │  (8 tools)       │
└──────────────────┘  └──────────────────┘
```

---

## 📊 Proposed MCP Server Groupings

Based on the existing `TOOL_GROUPS` in `model_capabilities.py`:

### 1. **MCP: Core Operations** (Port 8001)
**Tools (6)**:
- `list_templates`
- `launch_job_template`
- `get_job`
- `list_jobs`
- `health_check`
- `test_connection`

**Purpose**: Essential job execution and monitoring
**Target Models**: All models (135M+)

---

### 2. **MCP: Inventory Management** (Port 8002)
**Tools (5)**:
- `list_inventories`
- `get_inventory`
- `create_inventory`
- `sync_inventory`
- `delete_inventory`

**Purpose**: Inventory CRUD operations
**Target Models**: All models (135M+)

---

### 3. **MCP: Job Templates** (Port 8003)
**Tools (8)**:
- `create_job_template`
- `update_job_template`
- `delete_job_template`
- `list_hosts`
- `create_host`
- `get_host`
- `update_host`
- `delete_host`

**Purpose**: Template and host management
**Target Models**: Medium+ models (1.7B+)

---

### 4. **MCP: User Management** (Port 8004)
**Tools (6)**:
- `list_users`
- `get_user`
- `get_user_by_name`
- `create_user`
- `update_user`
- `delete_user`

**Purpose**: User administration
**Target Models**: Medium+ models (1.7B+)

---

### 5. **MCP: Project Management** (Port 8005)
**Tools (6)**:
- `list_projects`
- `get_project`
- `create_project`
- `update_project`
- `sync_project`
- `delete_project`

**Purpose**: SCM project management
**Target Models**: Medium+ models (1.7B+)

---

### 6. **MCP: Organization Management** (Port 8006)
**Tools (5)**:
- `list_organizations`
- `get_organization`
- `create_organization`
- `update_organization`
- `delete_organization`

**Purpose**: Organization administration
**Target Models**: Medium+ models (1.7B+)

---

### 7. **MCP: Schedule Management** (Port 8007)
**Tools (5)**:
- `list_schedules`
- `get_schedule`
- `create_schedule`
- `update_schedule`
- `delete_schedule`

**Purpose**: Job scheduling
**Target Models**: Large models (7B+)

---

### 8. **MCP: Advanced Operations** (Port 8008)
**Tools (8)** - Split into sub-categories:
- Credentials: `list_credentials`, `create_credential`, `update_credential`, `delete_credential`
- Workflows: `list_workflow_job_templates`, `create_workflow_job_template`, `launch_workflow_job_template`, `delete_workflow_job_template`

**Purpose**: Complex operations
**Target Models**: Large models (7B+)

---

### 9. **MCP: Notifications** (Port 8009)
**Tools (4)**:
- `list_notifications`
- `create_notification`
- `update_notification`
- `delete_notification`

**Purpose**: Notification template management
**Target Models**: Large models (7B+)

---

### 10. **MCP: Infrastructure** (Port 8010)
**Tools (4)**:
- `list_instance_groups`
- `create_instance_group`
- `update_instance_group`
- `delete_instance_group`

**Purpose**: Infrastructure management
**Target Models**: Large models (7B+)

---

## 🔧 Implementation Plan

### Phase 1: Foundation (Week 1)
**Goal**: Create shared infrastructure for multi-server architecture

#### 1.1 Create Shared Library Structure
```
mcp-server/
├── shared/                    # NEW: Shared components
│   ├── __init__.py
│   ├── awx_client.py         # Moved from adapters/awx_service.py
│   ├── config.py             # Shared config
│   ├── auth.py               # Shared authentication
│   ├── audit.py              # Shared audit logger
│   └── middleware.py         # Shared middleware
├── servers/                   # NEW: Individual MCP servers
│   ├── core/                 # Port 8001
│   │   ├── main.py
│   │   ├── routes.py
│   │   └── config.py
│   ├── inventory/            # Port 8002
│   │   ├── main.py
│   │   ├── routes.py
│   │   └── config.py
│   ├── templates/            # Port 8003
│   │   ├── main.py
│   │   ├── routes.py
│   │   └── config.py
│   └── ... (repeat for each server)
├── docker-compose.multi.yml  # NEW: Multi-server compose
├── k8s-multi/                # NEW: K8s manifests for all servers
└── gateway/                   # NEW: Smart routing gateway
    ├── main.py
    ├── router.py
    └── config.py
```

#### 1.2 Extract Shared Components
**Files to Create**:
- `shared/awx_client.py` - Base AWX client (copy from `app/adapters/awx_service.py`)
- `shared/config.py` - Shared configuration
- `shared/audit.py` - Shared audit logging
- `shared/auth.py` - Shared authentication logic

#### 1.3 Create Server Template
**Template Structure** (`servers/_template/`):
```python
# servers/_template/main.py
from fastapi import FastAPI
from shared.awx_client import awx_client
from shared.middleware import setup_middleware
from .routes import router

app = FastAPI(
    title="AWX MCP - {SERVER_NAME}",
    description="{DESCRIPTION}",
    version="2.0.0"
)

setup_middleware(app)
app.include_router(router)

@app.get("/health")
async def health():
    return {"status": "healthy", "server": "{SERVER_NAME}"}

@app.get("/ready")
async def ready():
    # Test AWX connection
    available = await awx_client.ping()
    return {"ready": available}
```

---

### Phase 2: Core Servers (Week 2)
**Goal**: Implement the 3 most critical servers + Update Open-WebUI tool

#### 2.1 Implement Core Operations Server (Port 8001) ✅ COMPLETE
**Priority**: HIGHEST - Essential for all operations

**Implementation**:
```bash
servers/core/
├── main.py           # FastAPI app ✅
├── routes.py         # Job execution endpoints ✅
├── schemas.py        # Pydantic models ✅
└── Dockerfile        # Containerization ✅
```

**Routes**:
- `POST /job_templates/{id}/launch` ✅
- `GET /job_templates` ✅
- `GET /jobs` ✅
- `GET /jobs/{id}` ✅
- `GET /health` ✅
- `GET /ready` ✅

**Status**: ✅ Deployed and tested on port 8001

#### 2.2 Implement Inventory Server (Port 8002)
**Priority**: HIGH - Common operation

**Implementation**:
```bash
servers/inventory/
├── main.py           # ✅ Structure created
├── routes.py         # ⏳ Needs customization
├── schemas.py        # ⏳ Needs customization
└── Dockerfile        # ✅ Created
```

#### 2.3 Implement Templates Server (Port 8003)
**Priority**: HIGH - Template management

**Implementation**:
```bash
servers/templates/
├── main.py           # ✅ Structure created
├── routes.py         # ⏳ Needs customization
├── schemas.py        # ⏳ Needs customization
└── Dockerfile        # ✅ Created
```

#### 2.4 Update Open-WebUI Tool for Multi-Server Architecture 🆕
**Priority**: HIGH - Client compatibility

**Implementation**:
- ✅ Created `open-webui-tool-multi-server.py`
- Features:
  - Automatic server selection based on operation
  - Gateway support (when implemented)
  - Direct connection to individual servers
  - Backward compatible with existing tool
  - Model optimization support

**Changes from Original**:
1. **Smart Routing**: Automatically routes requests to correct server
2. **Server Configuration**: Separate URLs for each specialized server
3. **Flexible Deployment**: Works with gateway OR individual servers
4. **Simplified Code**: Unified `_make_request()` method
5. **Better Error Messages**: Includes server information in errors

**Migration Path**:
- Keep `open-webui-tool.py` (original - points to monolith)
- Use `open-webui-tool-multi-server.py` (new - multi-server support)
- Both work during transition period
- Deprecate original after full migration

---

### Phase 3: Management Servers (Week 3)
**Goal**: Implement user, project, and organization servers

#### 3.1 User Management Server (Port 8004)
#### 3.2 Project Management Server (Port 8005)
#### 3.3 Organization Management Server (Port 8006)

**Follow same pattern as Phase 2**

---

### Phase 4: Advanced Servers (Week 4)
**Goal**: Implement schedule, advanced, notification, and infrastructure servers

#### 4.1 Schedule Management Server (Port 8007)
#### 4.2 Advanced Operations Server (Port 8008)
#### 4.3 Notifications Server (Port 8009)
#### 4.4 Infrastructure Server (Port 8010)

---

### Phase 5: Gateway & Orchestration (Week 5)
**Goal**: Create intelligent routing gateway

#### 5.1 Smart Gateway Implementation
**Purpose**: Route requests to appropriate MCP server based on operation

```python
# gateway/router.py
ROUTE_MAP = {
    "/job_templates": "core:8001",
    "/inventories": "inventory:8002",
    "/job_templates/{id}/create": "templates:8003",
    "/users": "users:8004",
    "/projects": "projects:8005",
    "/organizations": "orgs:8006",
    "/schedules": "schedules:8007",
    "/credentials": "advanced:8008",
    "/workflow_job_templates": "advanced:8008",
    "/notifications": "notifications:8009",
    "/instance_groups": "infrastructure:8010",
}
```

**Features**:
- Request routing based on path
- Load balancing across server instances
- Health checking
- Circuit breaker pattern
- Request aggregation (for multi-server queries)

#### 5.2 Service Discovery
**Options**:
1. **Static Configuration** (Simple, for MVP)
   - Environment variables with server URLs
   - Docker Compose service names

2. **Dynamic Discovery** (Production)
   - Consul/etcd for service registry
   - Kubernetes service discovery

---

### Phase 6: Deployment & Testing (Week 6)

#### 6.1 Docker Compose Configuration
**File**: `docker-compose.multi.yml`

```yaml
version: '3.8'

services:
  gateway:
    build: ./gateway
    ports:
      - "8000:8000"
    environment:
      - CORE_SERVER=http://core:8001
      - INVENTORY_SERVER=http://inventory:8002
      - TEMPLATES_SERVER=http://templates:8003
      # ... etc
    depends_on:
      - core
      - inventory
      - templates

  core:
    build: ./servers/core
    ports:
      - "8001:8001"
    environment:
      - AWX_BASE_URL=${AWX_BASE_URL}
      - AWX_TOKEN=${AWX_TOKEN}

  inventory:
    build: ./servers/inventory
    ports:
      - "8002:8002"
    environment:
      - AWX_BASE_URL=${AWX_BASE_URL}
      - AWX_TOKEN=${AWX_TOKEN}

  # ... repeat for all servers

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

#### 6.2 Kubernetes Deployment
**File**: `k8s-multi/deployment.yaml`

```yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: awx-mcp-core
spec:
  replicas: 2
  selector:
    matchLabels:
      app: awx-mcp
      component: core
  template:
    metadata:
      labels:
        app: awx-mcp
        component: core
    spec:
      containers:
      - name: core
        image: ghcr.io/antuelle78/awx_advanced_tools-core:latest
        ports:
        - containerPort: 8001
        env:
        - name: AWX_BASE_URL
          valueFrom:
            configMapKeyRef:
              name: awx-config
              key: base_url
---
# Repeat for each server with different component label
```

#### 6.3 Testing Strategy
**Unit Tests** (per server):
```bash
servers/core/tests/
├── test_routes.py
├── test_schemas.py
└── conftest.py
```

**Integration Tests** (gateway):
```bash
tests/integration/
├── test_gateway_routing.py
├── test_multi_server_operations.py
└── test_cross_server_dependencies.py
```

**Load Tests**:
```bash
tests/load/
├── test_concurrent_servers.py
└── test_gateway_performance.py
```

---

## 🔄 Migration Strategy

### Option 1: Big Bang Migration (NOT RECOMMENDED)
- Switch everything at once
- High risk
- Long testing period

### Option 2: Gradual Migration (RECOMMENDED)
**Phase A**: Keep existing server running
**Phase B**: Deploy new servers alongside
**Phase C**: Gradually migrate clients
**Phase D**: Deprecate old server

#### Detailed Gradual Migration

**Week 1-2**: Deploy Core + Inventory servers
- Run alongside existing monolith
- Test with small subset of users
- Monitor performance metrics

**Week 3-4**: Deploy Templates + Users servers
- Continue parallel operation
- Increase user migration (20-30%)

**Week 5-6**: Deploy remaining servers
- Migrate 50-70% of users
- Monitor for issues

**Week 7-8**: Full migration
- Migrate remaining users
- Deprecation warnings on old server

**Week 9**: Decommission monolith
- Archive old codebase
- Update documentation

---

## 📝 Code Changes Required

### 1. Refactor AWX Client
**Current**: `app/adapters/awx_service.py` (743 lines)
**New**: Split into:
```
shared/awx_client/
├── __init__.py
├── base.py           # Base client (connection, auth)
├── jobs.py           # Job operations
├── inventory.py      # Inventory operations
├── templates.py      # Template operations
├── users.py          # User operations
├── projects.py       # Project operations
├── organizations.py  # Organization operations
├── schedules.py      # Schedule operations
├── workflows.py      # Workflow operations
└── advanced.py       # Advanced operations
```

### 2. Update Model Capabilities
**Current**: `app/model_capabilities.py`
**New**: Add server recommendations

```python
# shared/model_capabilities.py

def get_recommended_servers(model_name: str) -> List[str]:
    """Get recommended MCP servers based on model capabilities."""
    capabilities = get_model_capabilities(model_name)

    servers = ["core", "inventory"]  # Always available

    if capabilities.max_tools >= 8:
        servers.extend(["templates", "users"])

    if capabilities.max_tools >= 12:
        servers.extend(["projects", "organizations"])

    if capabilities.complex_reasoning and capabilities.max_tools >= 15:
        servers.extend(["schedules"])

    if capabilities.max_tools >= 20 and capabilities.complex_reasoning:
        servers.extend(["advanced", "notifications", "infrastructure"])

    return servers
```

### 3. Update Context Manager
**New Feature**: Track server usage

```python
# shared/context_manager.py

@dataclass
class ServerUsage:
    server_name: str
    request_count: int
    success_rate: float
    avg_response_time: float

class ConversationContext:
    # ... existing fields
    server_usage: Dict[str, ServerUsage]

    def add_server_call(self, server_name: str, success: bool, response_time: float):
        """Track server usage patterns."""
        if server_name not in self.server_usage:
            self.server_usage[server_name] = ServerUsage(
                server_name=server_name,
                request_count=0,
                success_rate=1.0,
                avg_response_time=0.0
            )

        usage = self.server_usage[server_name]
        usage.request_count += 1
        # Update success rate and response time
        # ... implementation
```

---

## 🎯 Client Integration

### Open-WebUI Tool Updates

**Current**: Single tool connecting to one server
**New**: Multiple tools or smart routing

#### Option A: Multiple Tools (Simple)
Create separate tools in Open-WebUI:
- `AWX Core Operations`
- `AWX Inventory Management`
- `AWX Template Management`
- etc.

**Pros**:
- Clear separation
- User controls which to use
- Easy to implement

**Cons**:
- User needs to know which tool to use
- More configuration

#### Option B: Smart Gateway (Recommended)
Single tool that connects to gateway, which routes to appropriate server

**Tool Configuration**:
```python
# open-webui-tool-v2.py
class Valves(BaseModel):
    gateway_url: str = Field(
        default="http://localhost:8000",
        description="Gateway URL that routes to specialized servers"
    )
    # Remove individual server URLs
```

**Pros**:
- Transparent to user
- Single configuration
- Gateway handles complexity

**Cons**:
- Gateway is single point of failure (mitigate with HA)

---

## 📊 Performance Improvements Expected

### For Small Models (135M-1.7B)
**Current**:
- Overwhelmed by 40+ tool descriptions
- Context window filled quickly
- Poor performance

**After Refactoring**:
- Only 5-6 tools per server
- Clearer context
- **Expected: 50-70% improvement in response quality**

### For Medium Models (3B-8B)
**Current**:
- Progressive tool loading helps but still complex
- Multiple tools compete for attention

**After Refactoring**:
- Focused tool sets
- Better reasoning about specific domains
- **Expected: 30-40% improvement**

### For Large Models (20B+)
**Current**:
- Handle well but could be better organized

**After Refactoring**:
- Clearer organization
- Parallel server access possible
- **Expected: 10-20% improvement**

---

## 🔐 Security Considerations

### 1. Inter-Server Communication
**Requirement**: Servers may need to call each other

**Solution**: Shared authentication token
```python
# shared/auth.py
INTERNAL_TOKEN = os.getenv("INTERNAL_AUTH_TOKEN")

def verify_internal_request(request: Request) -> bool:
    token = request.headers.get("X-Internal-Token")
    return token == INTERNAL_TOKEN
```

### 2. Per-Server Access Control
**Requirement**: Different users need different server access

**Solution**: Role-based access in gateway
```python
# gateway/acl.py
SERVER_ACCESS = {
    "admin": ["*"],  # All servers
    "operator": ["core", "inventory", "templates"],
    "viewer": ["core"],  # Read-only operations only
}
```

### 3. Audit Logging
**Requirement**: Track which server handled which request

**Enhancement**:
```python
# shared/audit.py
def audit(
    user: str,
    action: str,
    server: str,  # NEW: Track server
    platform: str,
    request: dict,
    response: dict | None = None,
    error: str | None = None,
):
    entry = {
        "user": user,
        "action": action,
        "server": server,  # NEW
        "platform": platform,
        # ... rest of fields
    }
```

---

## 🧪 Testing Plan

### 1. Unit Tests (Per Server)
**Coverage Target**: 90%+

```bash
# Test each server independently
pytest servers/core/tests/ --cov=servers/core
pytest servers/inventory/tests/ --cov=servers/inventory
# ... etc
```

### 2. Integration Tests (Cross-Server)
**Scenarios**:
- User creates inventory → User creates host in that inventory (inventory + templates servers)
- User creates project → User creates template using that project (projects + templates servers)
- User creates schedule → Schedule launches job template (schedules + core servers)

### 3. Performance Tests
**Metrics**:
- Response time per server
- Gateway routing overhead
- Concurrent request handling
- Memory usage per server

**Tools**:
- Locust for load testing
- Prometheus for metrics
- Grafana for visualization

### 4. Failure Scenario Tests
**Scenarios**:
- One server down (gateway should route around)
- Gateway down (direct server access)
- AWX down (all servers should handle gracefully)
- Partial network failure

---

## 📈 Monitoring & Observability

### 1. Per-Server Metrics
**Metrics to Track**:
```python
# servers/core/metrics.py
from prometheus_client import Counter, Histogram

request_count = Counter(
    'awx_mcp_requests_total',
    'Total requests',
    ['server', 'endpoint', 'status']
)

request_duration = Histogram(
    'awx_mcp_request_duration_seconds',
    'Request duration',
    ['server', 'endpoint']
)
```

### 2. Gateway Metrics
**Additional Metrics**:
- Routing decisions
- Server health checks
- Failed routings
- Circuit breaker activations

### 3. Dashboard
**Grafana Dashboard Sections**:
1. Overall health (all servers)
2. Per-server performance
3. Gateway routing efficiency
4. Error rates and types
5. Model performance by server

---

## 💰 Cost-Benefit Analysis

### Costs
**Development Time**: 6 weeks (1 developer)
**Infrastructure**: Additional containers/pods (estimated 2x current resources)
**Maintenance**: Slightly higher complexity
**Migration Risk**: Moderate (mitigated by gradual approach)

### Benefits
**Performance**: 30-70% improvement for small models
**Scalability**: Independent scaling of high-traffic servers
**Maintainability**: Clearer code organization
**Security**: Better access control granularity
**Testing**: Easier to test individual components
**Development**: Parallel development possible

### ROI Calculation
**Assumptions**:
- 100 users, 50% using small models
- Current: 60% satisfaction with small models
- After: 90% satisfaction

**Value**:
- Improved user experience: HIGH
- Reduced support burden: MEDIUM
- Better scalability: HIGH
- Code maintainability: HIGH

**Recommendation**: **PROCEED** - Benefits significantly outweigh costs

---

## 🚀 Quick Start Implementation

### Minimum Viable Product (MVP) - 2 Weeks

**Goal**: Prove concept with 3 servers

#### Week 1: Foundation
1. Extract shared AWX client
2. Create server template
3. Implement Core Operations server (8001)
4. Implement Inventory server (8002)

#### Week 2: Testing & Deployment
5. Create simple gateway (no smart routing, just proxy)
6. Docker Compose configuration
7. Basic tests
8. Deploy alongside existing server

**Success Criteria**:
- 2 servers running independently
- Gateway routes requests correctly
- Basic operations work
- Performance metrics show improvement

---

## 📚 Documentation Updates Required

### 1. Architecture Docs
- Update architecture diagrams
- Document server responsibilities
- Inter-server communication patterns

### 2. API Documentation
- Per-server OpenAPI specs
- Gateway API documentation
- Migration guide for clients

### 3. Deployment Guides
- Docker Compose multi-server setup
- Kubernetes multi-server deployment
- Scaling guidelines

### 4. Developer Guide
- How to add new server
- Shared library usage
- Testing guidelines

---

## 🎓 Recommendations

### Priority Order
1. **HIGH PRIORITY**: Core Operations + Inventory + Templates (80% of usage)
2. **MEDIUM PRIORITY**: Users + Projects + Organizations (15% of usage)
3. **LOW PRIORITY**: Advanced servers (5% of usage, complex operations)

### Phased Approach
**Phase 1 (MVP - 2 weeks)**: Core + Inventory
**Phase 2 (Essential - 2 weeks)**: Templates + Users
**Phase 3 (Complete - 2 weeks)**: Remaining servers + Gateway
**Phase 4 (Polish - 2 weeks)**: Performance tuning + Documentation

### Risk Mitigation
1. **Run parallel systems** during migration
2. **Feature flags** to toggle between old/new
3. **Comprehensive monitoring** from day 1
4. **Rollback plan** ready
5. **Gradual user migration** (10% → 30% → 70% → 100%)

### Success Metrics
- **Performance**: 30%+ improvement for small models
- **Reliability**: 99.9% uptime per server
- **Adoption**: 80%+ users migrated within 2 months
- **Satisfaction**: NPS score increase

---

## ✅ Conclusion

This refactoring addresses the fundamental issue of tool overload for smaller LLMs by creating **focused, specialized MCP servers**. The gradual migration approach minimizes risk while the modular architecture provides better scalability, maintainability, and performance.

**Recommended Next Steps**:
1. Review and approve this plan
2. Set up development environment
3. Start Phase 1 (MVP) implementation
4. Schedule weekly review meetings
5. Begin documentation updates

**Estimated Timeline**: 6-8 weeks for complete implementation
**Risk Level**: Medium (mitigated by gradual approach)
**Expected ROI**: High (significant performance improvement for 50% of users)