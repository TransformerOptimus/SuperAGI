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
    response = test_app.get("/get/list")
    assert response.status_code == 200

def test_get_marketplace_vectordb_list(test_app):
    response = test_app.get("/marketplace/list")
    assert response.status_code == 200

def test_get_user_connected_vector_db_list(test_app):
    response = test_app.get("/user/list")
    assert response.status_code == 200

def test_get_vector_db_details(test_app):
    response = test_app.get("/get/db/details/1")  # Assuming we have a vector db with id 1
    assert response.status_code == 200

def test_delete_vector_db(test_app):
    # Assuming we have a vector db with id 1 and it's deletable
    response = test_app.post("/delete/1") 
    assert response.status_code == 200

def test_connect_pinecone_vector_db(test_app):
    response = test_app.post("/connect/pinecone", data=json.dumps(sample_data))
    assert response.status_code == 200
    assert response.json()["success"] == True

def test_connect_qdrant_vector_db(test_app):
    response = test_app.post("/connect/qdrant", data=json.dumps(sample_data))
    assert response.status_code == 200
    assert response.json()["success"] == True

def test_update_vector_db(test_app):
    # Assuming we have a vector db with id 1 and it's updatable
    response = test_app.put("/update/vector_db/1", data=json.dumps({"new_indices": ["index1", "index2"]}))
    assert response.status_code == 200   