import pytest
from unittest.mock import MagicMock
from fastapi import status
from fastapi.testclient import TestClient
from superagi.models.knowledge_configs import KnowledgeConfigs
from main import app

client = TestClient(app)

def test_get_marketplace_knowledge_configs_details(mocker):
    knowledge_id = 1
    mock_knowledge_configs = [
        KnowledgeConfigs(knowledge_id=1, obj1='test11', obj2='test12'),
        KnowledgeConfigs(knowledge_id=1, obj1='test21', obj2='test22')
    ]

    # Mock the query function
    mock_query = mocker.patch('fastapi_sqlalchemy.db.session.query')
    mock_query.return_value.filter.return_value.all.return_value = mock_knowledge_configs

    response = client.get(f"/marketplace/details/{knowledge_id}")

    assert response.status_code == 200
    assert len(response.json()) == 2
    for i, data in enumerate(response.json()):
        assert data["knowledge_id"] == knowledge_id
        assert data["obj1"] == mock_knowledge_configs[i].obj1
        assert data["obj2"] == mock_knowledge_configs[i].obj2

def test_get_marketplace_knowledge_configs_details_not_found(mocker):
    knowledge_id = 1

    # Mock the query function
    mock_query = mocker.patch('fastapi_sqlalchemy.db.session.query')
    mock_query.return_value.filter.return_value.all.return_value = []

    response = client.get(f"/marketplace/details/{knowledge_id}")
    assert response.status_code == 404