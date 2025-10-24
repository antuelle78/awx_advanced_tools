# AWX Advanced Tools - An LLM-Enabled Gateway for Ansible AWX

> **TL;DR** – A lightweight FastAPI service that acts as a gateway between a Large Language Model (LLM) and Ansible AWX. It exposes a REST API that allows LLMs to launch job templates, create inventories, and query job statuses.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Design](#architecture--design)
3. [Installation & Setup](#installation--setup)
4. [Configuration](#configuration)
5. [Running the Server](#running-the-server)
6. [API Specification](#api-specification)
7. [Open-WebUI Tool](#open-webui-tool)
8. [Testing](#testing)
9. [Deployment](#deployment)
10. [Contribution Guidelines](#contribution-guidelines)
11. [License](#license)
---

## 1. Project Overview

This repository contains a FastAPI application that serves as a bridge between an LLM and Ansible AWX. It allows an LLM to perform actions in AWX by calling a simple, secure REST API.

| Component | Purpose |
|-----------|---------|
| **FastAPI** | Web framework exposing the REST API and automatic OpenAPI docs. |
| **Pydantic** | Environment-variable loading and request validation. |
| **AWX Adapter** | Implements the three core AWX actions: `launch_job_template`, `create_inventory`, and `get_job`. |
| **LLM Client Factory** | Supports multiple LLM providers (e.g., OpenAI, Ollama) for generating AWX payloads. |
| **Docker Support** | Comes with `docker-compose.yml` for easy local development and a `Dockerfile` for production. |
| **Kubernetes Manifests** | Includes basic manifests for deploying to Kubernetes. |

---

## 2. Architecture & Design

The service exposes a standard REST API. An external tool, such as Open-WebUI, makes authenticated requests to this service, which then translates them into the appropriate calls to the AWX API.

### High-Level Flow
```
Client (e.g., Open-WebUI) → REST API (with Bearer token) → AWX Advanced Tools
   │
   ├─► Authenticate request
   ├─► Call corresponding AWX adapter method
   ├─► Make request to AWX API
   └─► Return JSON response
```

---

## 3. Installation & Setup

### 3.1 Prerequisites

| Component | Minimum Version |
|-----------|-----------------|
| Python    | 3.10+ |
| Docker    | 20.10+ |
| Redis     | 5.0+   |

### 3.2 Clone the Repository

```bash
git clone https://github.com/antuelle78/awx_advanced_tools.git
cd awx_advanced_tools
```

### 3.3 Docker Hub Image

A pre-built Docker image is available on Docker Hub:
```bash
docker pull antuelle78/awx_advanced_tools:latest
```

---

## 4. Configuration

All settings are read from environment variables. Create a `.env` file in the project root or set the variables in your deployment environment.

| Variable | Description | Example |
|----------|-------------|---------|
| `AWX_BASE_URL` | Base URL of your AWX/Tower instance. | `https://awx.example.com` |
| `AWX_TOKEN` | Bearer token with AWX permissions. | `your_awx_token` |
| `JWT_SECRET` | Secret used to validate JWTs for API access. | `a_very_secret_key` |
| `LLM_PROVIDER` | The LLM provider to use. Can be `default` (for OpenAI-compatible APIs) or `ollama`. | `ollama` |
| `LLM_ENDPOINT` | The endpoint of the LLM provider. | `http://host.docker.internal:11434` |
| `LLM_MODEL` | The name of the LLM model to use. | `gemma3` |
| `LLM_API_KEY` | API key for the LLM provider (only required for `default` provider). | `your_llm_api_key` |
| `REDIS_HOST` | The hostname of the Redis server. | `redis` |
| `REDIS_PORT` | The port of the Redis server. | `6379` |
| `REDIS_DB` | The Redis database to use. | `0` |

---

## 5. Running the Server

The easiest way to run the server is with Docker Compose, which also starts a mock AWX service for testing.

```bash
docker compose up -d
```

The server will be available at `http://localhost:8001`.

---

## 6. API Specification

The following endpoints are available:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/awx/job_templates/{template_id}/launch` | POST | Launches an AWX job template. |
| `/awx/inventories` | POST | Creates a new inventory in AWX. |
| `/awx/jobs/{job_id}` | GET | Retrieves the current status of a job. |
| `/docs` | GET | Swagger UI for interactive API documentation. |

---

## 7. Open-WebUI Tool

This repository includes an `open-webui-tool.py` file that can be imported into Open-WebUI to allow an LLM to use this service.

### Configuration

1.  Import the `open-webui-tool.py` file in the Open-WebUI interface.
2.  In the tool's "Valves" settings, enter a valid JWT for the `jwt_token` field. You can generate one using the `generate_token.py` script.

---

## 8. Testing

Run the automated tests with `pytest`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

---

## 9. Deployment

### Docker
You can run the pre-built image from Docker Hub:
```bash
docker run -d -p 8001:8000 \
  --env-file .env \
  antuelle78/awx_advanced_tools:latest
```

### Kubernetes
Basic Kubernetes manifests are provided in the `k8s` directory. Update the `deployment.yaml` to use the correct image:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
spec:
  template:
    spec:
      containers:
        - name: mcp-server
          image: antuelle78/awx_advanced_tools:latest
```

---

## 10. Contribution Guidelines

Pull requests are welcome! Please fork the repository and submit a pull request with your changes.

---

## 11. License

MIT License.