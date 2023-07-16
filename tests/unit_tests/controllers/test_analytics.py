# test_analytics.py
import pytest
from fastapi.testclient import TestClient
from superagi.apm.analytics import app
from superapi.helper.auth import AuthException

@pytest.fixture
def client():
    return TestClient(app)


def test_get_metrics(client):
    # Assuming you have a valid get_user_organisation object
    response = client.get("/metrics", dependencies=[Depends(get_user_organisation)])
    assert response.status_code == 200
    assert "total_tokens" in response.json()
    assert "total_calls" in response.json()
    assert "runs_completed" in response.json()

def test_get_agents(client):
    # Assuming you have a valid get_user_organisation object
    response = client.get("/agents/all", dependencies=[Depends(get_user_organisation)])
    assert response.status_code == 200
    assert "agents" in response.json()

def test_get_agent_runs(client):
    response = client.get("/agents/1", dependencies=[Depends(get_user_organisation)])
    assert response.status_code == 200
    assert "runs" in response.json()

def test_get_active_runs(client):
    response = client.get("/runs/active", dependencies=[Depends(get_user_organisation)])
    assert response.status_code == 200
    assert "active_runs" in response.json()

def test_get_tools_used(client):
    response = client.get("/tools/used", dependencies=[Depends(get_user_organisation)])
    assert response.status_code == 200
    assert "tools" in response.json()