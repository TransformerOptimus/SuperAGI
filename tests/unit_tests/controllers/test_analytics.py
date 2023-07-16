import pytest
import requests
from fastapi.testclient import TestClient
from main import app  # assuming your FastAPI app is defined here

client = TestClient(app)

def test_get_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "metrics" in response.json()

def test_get_agents():
    response = client.get("/agents/all")
    assert response.status_code == 200
    assert "agents" in response.json()

def test_get_agent_runs():
    response = client.get("/agents/1")  # assuming an agent with id 1 exists
    assert response.status_code == 200
    assert "runs" in response.json()

def test_get_active_runs():
    response = client.get("/runs/active")
    assert response.status_code == 200
    assert "active_runs" in response.json()

def test_get_tools_used():
    response = client.get("/tools/used")
    assert response.status_code == 200
    assert "tools_used" in response.json()