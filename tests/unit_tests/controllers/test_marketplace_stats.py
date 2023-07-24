import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException
from superagi.models.marketplace_stats import MarketPlaceStats
from main import app  # assuming the FastAPI app is defined in this file

client = TestClient(app)

def test_get_knowledge_download_number():
    # create a mock instance of MarketPlaceStats
    mocked_stats = Mock(spec=MarketPlaceStats)
    mocked_stats.value = 10
    with patch('superagi.endpoint.fastapi_sqlalchemy.db.session.query', return_value=mocked_stats) as mock: 
        # assuming successful case
        response = client.get("/knowledge/downloads/1")
        assert response.status_code == 200
        assert response.json() == mocked_stats.value

        # assuming there's no download information for the given knowledge_id
        mocked_stats.value = 0
        response = client.get("/knowledge/downloads/1")
        assert response.status_code == 200
        assert response.json() == mocked_stats.value