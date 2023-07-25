import pytest
from unittest.mock import MagicMock
from fastapi import status
from fastapi.testclient import TestClient
from superagi.models.knowledge_configs import KnowledgeConfigs
from main import app

client = TestClient(app)

def test_get_marketplace_knowledge_configs_details(mocker):
    knowledge_id = 1

    # Mock the query function
    mock_db = mocker.patch('superagi.controllers.knowledge_configs.db')
    mock_db.session.query.return_value.filter.return_value.all.return_value = []

    response = client.get(f"/knowledge_configs/marketplace/details/{knowledge_id}")
    assert response.status_code == 200