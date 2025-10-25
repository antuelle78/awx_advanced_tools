# tests/test_main.py
import os

# Set required environment variables for testing before importing
os.environ["JWT_SECRET"] = "test_secret"
os.environ["AWX_BASE_URL"] = "dummy"
os.environ["AWX_TOKEN"] = "dummy"
os.environ["LLM_ENDPOINT"] = "dummy"
os.environ["LLM_MODEL"] = "dummy"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Helper to get token


def get_token():
    response = client.post("/login", auth=("admin", "password"))
    assert response.status_code == 200
    return response.json()["access_token"]


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "running"}


def test_login_and_token():
    token = get_token()
    assert token
