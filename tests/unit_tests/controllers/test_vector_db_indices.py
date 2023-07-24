import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app # assume your FastAPI app is defined here
from superagi.models.vector_dbs import Vectordbs
from superagi.models.vector_db_indices import VectordbIndices

client = TestClient(app)

@patch('superagi.models.Vectordbs.get_vector_db_from_organisation')
@patch('superagi.models.Knowledges.fetch_knowledge_details_marketplace')
@patch('superagi.models.KnowledgeConfigs.fetch_knowledge_config_details_marketplace')
@patch('superagi.models.VectordbIndices.get_vector_indices_from_vectordb')
def test_get_marketplace_valid_indices(mock_indices, mock_knowledge_config, mock_knowledge, mock_vector_db):
    mock_vector_db.return_value = [{'id': 1, 'db_type': 'Pinecone'}, {'id': 2, 'db_type': 'Qdrant'}]
    mock_knowledge.return_value = {'id': 1}
    mock_knowledge_config.return_value = {'dimensions': 10}
    mock_indices.return_value = [{'id': 1, 'name': 'index1', 'dimensions': 10, 'state': 'Default'}, {'id': 2, 'name': 'index2', 'dimensions': 5, 'state': 'Custom'}]
    response = client.get('/get/marketplace/valid_indices/Knowledge1')
    assert response.status_code == 200
    assert response.json() == {'pinecone': [{'id': 1, 'name': 'index1', 'is_valid_dimension': True, 'is_valid_state': True}], 'qdrant': []}

@patch('superagi.models.Vectordbs.get_vector_db_from_organisation')
@patch('superagi.models.VectordbIndices.get_vector_indices_from_vectordb')
def test_get_user_valid_indices(mock_indices, mock_vector_db):
    mock_vector_db.return_value = [{'id': 1, 'db_type': 'Pinecone'}, {'id': 2, 'db_type': 'Qdrant'}]
    mock_indices.return_value = [{'id': 1, 'name': 'index1', 'dimensions': 10, 'state': 'Default'}, {'id': 2, 'name': 'index2', 'dimensions': 5, 'state': 'Custom'}]
    response = client.get('/get/user/valid_indices')
    assert response.status_code == 200
    assert response.json() == {'pinecone': [{'id': 1, 'name': 'index1', 'is_valid_state': True}], 'qdrant': []}