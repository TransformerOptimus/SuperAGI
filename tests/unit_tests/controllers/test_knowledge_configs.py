import pytest
from unittest.mock import MagicMock
from fastapi import status
from fastapi.testclient import TestClient
from superagi.models.knowledge_configs import KnowledgeConfigs
from main import app

client = TestClient(app)

def test_get_marketplace_knowledge_configs_details(mocker):
    knowledge_id = 1
    mock_knowledge_configs = MagicMock()
    # Mock the query function
    mock_db = mocker.patch('superagi.controllers.knowledge_configs.db')
    mock_db.session.query.return_value.filter.return_value.all.return_value = mock_knowledge_configs

    response = client.get(f"/marketplace/details/{knowledge_id}")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json() == mock_knowledge_configs

def test_get_marketplace_knowledge_configs_details_not_found(mocker):
    knowledge_id = 1

    # Mock the query function
    mock_db = mocker.patch('superagi.controllers.knowledge_configs.db')
    mock_db.session.query.return_value.filter.return_value.all.return_value = []

    response = client.get(f"/marketplace/details/{knowledge_id}")
    assert response.status_code == 404