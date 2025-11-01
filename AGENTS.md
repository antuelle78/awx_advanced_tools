# AGENTS.md

## Build / Lint / Test
- **Build**: `docker compose build`
- **Run**: `docker compose up -d`
- **Lint**: `ruff check . --fix`
- **Format**: `ruff format .`
- **Type-check**: `mypy --explicit-package-bases --ignore-missing-imports app`
- **Security scan**: `safety scan && bandit -r app/`
- **Run all tests**: `pytest`
- **Run single test**: `pytest tests/test_<module>.py -v`
- **Run tests by pattern**: `pytest -k <pattern>`
- **Coverage**: `pytest --cov=app --cov-report term-missing`

## Style Guidelines
- **Imports**: stdlib → 3rd-party → local (use `isort`)
- **Formatting**: `ruff format` (line-length 88)
- **Naming**: snake_case vars/functions, CamelCase classes, UPPER_CASE constants
- **Type hints**: `pydantic.BaseModel` for schemas; standard typing otherwise
- **Error handling**: `FastAPI.HTTPException` for client errors; custom exceptions for internal logic
- **Logging**: `logging` module, JSON output, INFO level
- **Docstrings**: one-line for public functions
- **Async**: Use async/await for I/O operations

## CI / PR
- All PRs run `ruff`, `mypy`, `pytest`, security scans
- Do not change `requirements.txt` unless needed
- Keep API backwards compatible
- No Cursor or Copilot rules in this repo

---

# 📊 Codebase Analysis: AWX Advanced Tools MCP Server

## 🎯 Project Overview

**AWX Advanced Tools** is an intelligent bridge between Large Language Models (LLMs) and Ansible AWX/Tower automation infrastructure. It exposes AWX management capabilities through a REST API with AI-powered features including model-aware tool discovery, context management, and enterprise-grade safety features.

**Purpose**: Enable LLMs to become AWX super administrators through natural language commands while maintaining security, reliability, and performance.

## 📐 Architecture Summary

```
┌─────────────────────┐
│  LLM/Open-WebUI     │
│  (Chat Interface)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Nginx Gateway      │ ← Basic Auth Layer
│  (Port 8001)        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   FastAPI Server    │
│   (MCP Server)      │
├─────────────────────┤
│ • Model Capabilities│ ← Intelligence Layer
│ • Context Manager   │
│ • Fallback Handler  │
│ • LLM Service       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   AWX Client        │ ← Adapter Layer
│  (HTTP/REST)        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   AWX/Tower API     │
└─────────────────────┘
```

## 📁 Codebase Structure

### Statistics
- **Total Python files**: 2,029 files
- **Lines of code (app/)**: ~3,016 lines
- **Test files**: 39 test cases
- **Python versions supported**: 3.10, 3.11, 3.12

### Directory Structure
```
mcp-server/
├── app/
│   ├── adapters/          # Service adapters (AWX, LLM, EV, SN)
│   │   ├── awx_service.py # Core AWX client (743 lines)
│   │   ├── awx.py         # FastAPI routes
│   │   ├── llm.py         # LLM endpoints
│   │   ├── audit.py       # Audit logging routes
│   │   ├── ev.py          # External validation
│   │   └── sn.py          # ServiceNow integration
│   ├── llm/              # LLM integration layer
│   │   ├── client.py     # OpenAI/Ollama clients
│   │   ├── service.py    # Prompt orchestration
│   │   ├── cache.py      # Response caching
│   │   └── templates.py  # Prompt templates
│   ├── audit/            # Audit logging
│   │   └── logger.py     # JSON audit logs
│   ├── schema/           # Schema validation
│   │   ├── registry.py   # Schema registry
│   │   └── validator.py  # JSON schema validation
│   ├── context/          # Context management
│   │   └── adapter.py    # Context adapters
│   ├── config.py         # Pydantic settings
│   ├── main.py           # FastAPI app entry
│   ├── model_capabilities.py  # Model-aware features (252 lines)
│   ├── context_manager.py     # Conversation context (214 lines)
│   └── fallback_handler.py    # Fallback logic (214 lines)
├── tests/                # Comprehensive test suite
├── prompts/              # LLM prompt templates
├── k8s/                  # Kubernetes manifests
├── .github/workflows/    # CI/CD pipeline
└── docs/                 # Documentation
```

## 🎨 Key Features & Innovations

### 1. Model-Aware Capabilities (`model_capabilities.py`)
**Brilliance**: Dynamically adjusts available tools based on LLM model size and capabilities.

```python
# Supports 8 model configurations from 135M to 20B parameters
MODEL_CAPABILITIES = {
    "smollm2:135m": {max_tools: 3, complex_reasoning: False},
    "granite3.1-dense:8b": {max_tools: 25, complex_reasoning: True},
    # ... progressive capability scaling
}
```

**Features**:
- Progressive tool exposure (basic → inventory → advanced)
- Context window management
- JSON accuracy assessment
- Concurrent tool call limits
- Simplified prompts for smaller models

### 2. Context Manager (`context_manager.py`)
**Brilliance**: Tracks conversation history and optimizes context for different model sizes.

**Features**:
- Tool call history with success metrics
- Automatic context pruning
- Conversation summaries
- Success rate tracking
- Response simplification triggers

### 3. Fallback Handler (`fallback_handler.py`)
**Brilliance**: Graceful degradation for complex operations on smaller models.

**Features**:
- Operation complexity assessment
- Simplified step-by-step guidance
- Automatic fallback selection
- Response simplification (aggressive/moderate)
- Security-aware recommendations

### 4. Comprehensive AWX Client (`awx_service.py`)
**Coverage**: 40+ AWX operations across all resource types

**Resources Managed**:
- Job Templates & Jobs
- Inventories & Hosts
- Projects & Organizations
- Users & Credentials
- Schedules & Workflows
- Notifications & Instance Groups
- Activity Stream

**Safety Features**:
- Dry-run modes for all destructive operations
- Confirmation requirements (`confirm=true`)
- Post-operation verification
- Input validation with Pydantic
- Comprehensive error handling

### 5. LLM Integration (`llm/`)
**Flexibility**: Supports multiple LLM providers with unified interface

**Providers**:
- OpenAI-compatible APIs
- Ollama (local models)
- Extensible base class pattern

**Features**:
- Temperature control per operation
- JSON-mode responses
- Response caching
- Schema validation
- Prompt templates

### 6. Audit Logging (`audit/logger.py`)
**Compliance**: Complete audit trail for enterprise environments

**Captures**:
- User actions
- Platform (AWX/EV/SN)
- Request/response payloads
- Errors and timestamps
- Daily log rotation

## 🔒 Security & Safety

### Authentication
- Nginx gateway with HTTP Basic Auth
- JWT support (configurable)
- AWX token or username/password auth
- Environment-based credential management

### Operation Safety
1. **Dry-run Mode**: Test operations without execution
2. **Confirmation Prompts**: Required for destructive actions
3. **Existence Checks**: Prevent duplicate resource creation
4. **Input Validation**: Pydantic models for all inputs
5. **Post-op Verification**: Confirm deletions completed

### Security Scanning
- Safety (dependency vulnerabilities)
- Bandit (code security)
- Trivy (container vulnerabilities)
- CodeQL analysis in CI/CD

## 🧪 Testing & Quality

### Test Coverage
- 39 test cases across 8 test modules
- Unit tests for all major components
- Integration tests for AWX operations
- Async/await pattern testing
- Coverage reporting to Codecov

### CI/CD Pipeline (`.github/workflows/ci.yml`)
**Comprehensive 295-line workflow**:

**Stages**:
1. **Lint**: Ruff formatting/linting (Python 3.10-3.12)
2. **Type-check**: MyPy static analysis
3. **Security**: Safety + Bandit scans
4. **Test**: Pytest with coverage
5. **Build**: Docker multi-stage build + Trivy scan
6. **Push**: GitHub Container Registry
7. **Deploy**: Staging (auto) + Production (on release)
8. **Release**: Automated GitHub releases

**Features**:
- Matrix builds (3 Python versions)
- Dependency caching
- Docker layer caching
- Parallel job execution
- Kubernetes deployment automation

## 🚀 Deployment Options

### 1. Docker Compose (Development)
```yaml
services:
  mcp-server:   # FastAPI app
  gateway:      # Nginx proxy
  redis:        # Caching (optional)
```

### 2. Kubernetes (Production)
**Manifests**: `k8s/`
- Deployment (2 replicas)
- Service (NodePort 30080)
- ConfigMap (environment config)
- PVC (audit logs persistence)
- Redis StatefulSet

### 3. Bare Docker
Pre-built images available:
- `ghcr.io/antuelle78/awx_advanced_tools:latest`
- `antuelle78/awx_advanced_tools:latest`

## 💡 Intelligent Design Patterns

### 1. Progressive Tool Exposure
Small models get basic tools first, advanced features unlocked as conversation progresses.

### 2. Adapter Pattern
Clean separation between:
- FastAPI routes (`adapters/awx.py`)
- Service logic (`adapters/awx_service.py`)
- External systems (AWX, LLM, ServiceNow)

### 3. Factory Pattern
LLM client selection based on provider configuration.

### 4. Singleton Pattern
Global instances: `awx_client`, `context_manager`, `fallback_handler`

### 5. Strategy Pattern
Different LLM clients (OpenAI/Ollama) implement common interface.

## 📊 Performance Optimizations

1. **Async/Await**: All I/O operations are async
2. **Connection Pooling**: httpx AsyncClient
3. **Response Caching**: In-memory cache for LLM responses
4. **Redis Integration**: Ready for distributed caching
5. **Context Pruning**: Automatic old context cleanup
6. **Batch Operations**: Model-specific batch size recommendations

## 🎯 Tool Groups & Capabilities

```python
TOOL_GROUPS = {
    "basic": [6 tools]           # Available immediately
    "inventory": [5 tools]        # After 1 conversation
    "users": [6 tools]            # Models ≥8 tools
    "projects": [6 tools]         # Models ≥12 tools
    "organizations": [5 tools]    # Models ≥12 tools
    "schedules": [5 tools]        # Models ≥15 tools + reasoning
    "advanced": [19 tools]        # Models ≥20 tools + reasoning
}
```

## 🔧 Configuration

**Environment Variables** (`.env`):
```bash
# AWX Configuration
AWX_BASE_URL=https://awx.example.com
AWX_TOKEN=your_awx_token
AWX_USERNAME=admin
AWX_PASSWORD=password

# LLM Configuration
LLM_PROVIDER=ollama|default
LLM_ENDPOINT=http://host.docker.internal:11434
LLM_MODEL=granite3.1-dense:8b
LLM_API_KEY=your_api_key

# Infrastructure
AUDIT_LOG_DIR=/var/log/mcp
REDIS_HOST=redis
JWT_SECRET=secret_key
```

## 🎨 API Design

### RESTful Endpoints
- `/awx/*` - AWX operations (40+ endpoints)
- `/llm/*` - LLM services (validate, generate, summarize)
- `/audit/*` - Audit log queries
- `/activity_stream` - AWX activity monitoring
- `/health` - Liveness check
- `/ready` - Readiness check (includes AWX ping)

### Pydantic Models
Strong typing for all request/response bodies:
- `InventoryCreate`, `UserCreate`, `ProjectCreate`
- `OrganizationUpdate`, `ProjectUpdate`, etc.

## 📈 Strengths

1. ✅ **Intelligent Model Adaptation**: Automatic tool selection based on LLM capabilities
2. ✅ **Enterprise-Grade Safety**: Dry-run, confirmation, audit logging
3. ✅ **Comprehensive Coverage**: 40+ AWX operations
4. ✅ **Production-Ready**: CI/CD, K8s manifests, monitoring
5. ✅ **Extensible Architecture**: Clean adapters for new integrations (EV, SN)
6. ✅ **Multi-Provider LLM**: OpenAI and Ollama support
7. ✅ **Context Management**: Conversation-aware optimization
8. ✅ **Graceful Degradation**: Fallback handlers for small models
9. ✅ **Testing**: Comprehensive test coverage
10. ✅ **Documentation**: Detailed README and inline docs

## 🔍 Areas for Potential Enhancement

1. **Redis Integration**: Currently optional, could enable distributed caching
2. **Rate Limiting**: No explicit rate limiting implemented
3. **Metrics/Observability**: Prometheus client imported but not fully utilized
4. **WebSocket Support**: Real-time job status updates
5. **Multi-tenancy**: No tenant isolation currently
6. **Advanced Caching**: LLM cache is in-memory only
7. **Error Recovery**: No automatic retry mechanisms
8. **API Versioning**: Single version currently

## 🏆 Innovation Highlights

### Model-Aware Tool Discovery
This is genuinely innovative. Most LLM tools expose all capabilities regardless of model size, leading to context overflow and poor performance on smaller models. This system:
- Profiles 8 different model sizes (135M to 20B parameters)
- Dynamically adjusts available tools
- Provides simplified prompts for complex operations
- Tracks success rates to optimize future interactions

### Fallback Handler Pattern
Unique approach to handling model limitations:
- Detects when operations are too complex for current model
- Provides step-by-step guidance instead of failing
- Recommends alternative approaches
- Simplifies responses based on success rate

### Conversation Context Management
Beyond simple chat history:
- Tracks tool usage patterns
- Calculates success rates per tool
- Triggers response simplification on poor performance
- Maintains optimal context window per model

## 🎓 Code Quality Assessment

**Architecture**: ⭐⭐⭐⭐⭐ (5/5)
- Clean separation of concerns
- Well-defined adapter layer
- Extensible design patterns

**Testing**: ⭐⭐⭐⭐ (4/5)
- Good coverage (39 tests)
- Async testing support
- Could use more integration tests

**Documentation**: ⭐⭐⭐⭐⭐ (5/5)
- Comprehensive README
- Inline docstrings
- Architecture diagrams
- Setup guides

**Security**: ⭐⭐⭐⭐⭐ (5/5)
- Multiple authentication layers
- Comprehensive safety features
- Security scanning in CI/CD
- Audit logging

**DevOps**: ⭐⭐⭐⭐⭐ (5/5)
- Excellent CI/CD pipeline
- K8s production deployment
- Multi-environment support
- Container security scanning

## 📝 Recommendations

### For Production Use
1. Enable Redis for distributed caching
2. Implement rate limiting per user/model
3. Add Prometheus metrics endpoints
4. Configure log aggregation (ELK/Loki)
5. Set up alert thresholds for audit logs

### For Development
1. Add integration tests with AWX test instance
2. Document adapter extension pattern
3. Create example custom prompts
4. Add performance benchmarks
5. Document model capability tuning

## 🎯 Use Cases

1. **DevOps Automation**: "Create a backup schedule for production servers"
2. **Incident Response**: "Launch emergency patching workflow"
3. **Infrastructure Provisioning**: "Deploy staging environment from template"
4. **Compliance Reporting**: "Show all job executions in the last 24 hours"
5. **User Management**: "Create developer access for the QA team"

## 📚 Technology Stack

**Core**:
- FastAPI 0.115+ (web framework)
- Pydantic 2.8 (validation)
- httpx 0.27 (async HTTP)
- uvicorn 0.30 (ASGI server)

**LLM**:
- OpenAI SDK
- Ollama SDK
- JSON schema validation

**Infrastructure**:
- Docker & Docker Compose
- Kubernetes (production)
- Nginx (gateway)
- Redis (caching)

**Observability**:
- Prometheus client
- JSON audit logs
- Health/readiness endpoints

**Testing**:
- pytest + pytest-asyncio
- pytest-cov (coverage)
- Ruff (linting)
- MyPy (type checking)
- Safety & Bandit (security)

## 🌟 Final Assessment

This is a **well-architected, production-ready system** that solves a real problem: making infrastructure automation accessible through natural language while maintaining enterprise security standards. The model-aware capabilities and fallback handling are genuinely innovative approaches to LLM integration.

**Maturity Level**: Production-ready
**Innovation Level**: High
**Code Quality**: Excellent
**Documentation**: Comprehensive
**Deployment Readiness**: ✅ Complete

The system demonstrates deep understanding of both LLM limitations and enterprise operational requirements, bridging them elegantly through intelligent adaptation and safety features.