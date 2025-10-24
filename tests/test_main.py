# tests/test_main.py
import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Helper to get token

def get_token():
    response = client.post("/login", data={"username": "alice", "password": "secret"})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "running"}


def test_login_and_token():
    token = get_token()
    assert token

