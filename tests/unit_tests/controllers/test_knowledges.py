from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi_sqlalchemy import db
from fastapi import APIRouter
from datetime import datetime
from main import app  # replace this with the actual FastAPI module

client = TestClient(app)
organisation_mock = {"id": 1, "name": "test_org"}

@patch("Knowledges.fetch_marketplace_list")
@patch("Knowledges.get_knowledge_install_details")
@patch("superagi.models.marketplace_stats.MarketPlaceStats.get_knowledge_installation_number")
def test_get_knowledge_list(mock_get_knowledge_install_number, mock_get_knowledge_install_details, mock_fetch_marketplace_list):
    # Arrange
    mock_fetch_marketplace_list.return_value = [{"id": 101, "name": "knowledge_1"}, {"id": 102, "name": "knowledge_2"}]
    mock_get_knowledge_install_details.return_value = [{"id": 101, "name": "knowledge_1"}, {"id": 102, "name": "knowledge_2"}]
    mock_get_knowledge_install_number.return_value = 5
    
    # Act
    response = client.get("/get/list", headers={"organisation": organisation_mock})
    
    # Assert
    assert response.status_code == 200
    assert response.json() == [
        {"id": 101, "name": "knowledge_1", "install_number": 5},
        {"id": 102, "name": "knowledge_2", "install_number": 5}
    ]

