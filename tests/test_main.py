# tests/test_main.py
import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.context.manager import ContextManager

@pytest.fixture(autouse=True)
def clear_context_before_test():
    ContextManager.clear_context()
    yield
    ContextManager.clear_context()

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

# Test a protected endpoint (e.g., context create)

def test_context_create_and_read():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    # create
    resp = client.post("/context/create", json={"ctx_id": "testctx", "data": {"foo": "bar"}}, headers=headers)
    assert resp.status_code == 200
    # read
    resp = client.get("/context/read/testctx", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == {"foo": "bar"}

# Clean up after test

def test_context_delete():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    # create a context to delete
    client.post("/context/create", json={"ctx_id": "testctx_del", "data": {"foo": "bar"}}, headers=headers)
    resp = client.delete("/context/delete/testctx_del", headers=headers)
    assert resp.status_code == 200
    # read should now fail
    resp = client.get("/context/read/testctx_del", headers=headers)
    assert resp.status_code == 404 or resp.status_code == 500
