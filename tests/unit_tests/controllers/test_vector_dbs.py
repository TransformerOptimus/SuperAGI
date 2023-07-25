import pytest
from fastapi.testclient import TestClient
from fastapi_sqlalchemy import db
from main import app  # assuming your FastAPI instance is named app
import json

client = TestClient(app)

# Sample structured data for testing
sample_data = {
    "api_key": "test_api_key",
    "environment": "test_environment",
    "collections": [
        "test_collection1",
        "test_collection2"
    ],
    "name": "test_db"
}

@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)
    yield client  # testing happens here

def test_get_vector_db_list(test_app):
    response = test_app.get("/vector_dbs/get/list")
    assert response.status_code == 200

def test_get_marketplace_vectordb_list(test_app):
    response = test_app.get("/vector_dbs/marketplace/list")
    assert response.status_code == 200

def test_get_user_connected_vector_db_list(test_app):
    response = test_app.get("/vector_dbs/user/list")
    assert response.status_code == 200

def test_delete_vector_db(test_app):
    # Assuming we have a vector db with id 1 and it's deletable
    response = test_app.post("/vector_dbs/delete/1") 
    assert response.status_code == 200
