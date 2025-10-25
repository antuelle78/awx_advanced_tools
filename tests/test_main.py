# tests/test_main.py
import os

# Set required environment variables for testing before importing
os.environ["AWX_BASE_URL"] = "dummy"
os.environ["AWX_TOKEN"] = "dummy"
os.environ["LLM_ENDPOINT"] = "dummy"
os.environ["LLM_MODEL"] = "dummy"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "running"}
