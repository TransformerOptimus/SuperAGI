import pytest
from unittest.mock import MagicMock, patch
from pinecone import UnauthorizedException
from superagi.vector_store.vector_factory import VectorFactory
from superagi.types.vector_store_types import VectorStoreType
from superagi.vector_store.pinecone import Pinecone
from superagi.vector_store.qdrant import Qdrant

PINECONE = 'pinecone'
WEAVIATE = 'weaviate'
QDRANT = 'qdrant'

def test_pinecone_vector_storage(monkeypatch):
    monkeypatch.setattr('superagi.config.config.get_config', MagicMock(return_value='some_key'))
    # assuming an embeding model class exist
    embedding_model = MagicMock()
    embedding_model.get_embedding.return_value = [0.1, 0.2, 0.3]
    
    with patch('superagi.vector_store.pinecone.pinecone.init') as mock_init:
        vector_storage = VectorFactory.get_vector_storage(PINECONE, 'index_name', embedding_model)
        assert isinstance(vector_storage, Pinecone)
        mock_init.assert_called_once()

def test_qdrant_vector_storage():
    embedding_model = MagicMock()
    embedding_model.get_embedding.return_value = [0.1, 0.2, 0.3]
    
    with patch('superagi.vector_store.qdrant.create_qdrant_client') as mock_client:
        vector_storage = VectorFactory.get_vector_storage(QDRANT, 'index_name', embedding_model)
        assert isinstance(vector_storage, Qdrant)
        mock_client.assert_called_once()

def test_unsupported_vector_store():
    with pytest.raises(ValueError):
        VectorFactory.get_vector_storage('unsupported', 'index_name', 'model')
        
def test_pinecone_build_vector_storage():
    index_name = "index_name"
    embedding_model = MagicMock()

    with patch('superagi.vector_store.pinecone.pinecone.init') as mock_init, \
        patch('superagi.vector_store.pinecone.pinecone.Index') as mock_index:
        mock_index.return_value = MagicMock()
        vector_storage = VectorFactory.build_vector_storage(PINECONE, index_name, embedding_model, api_key='some_key', environment='some_env')
        assert isinstance(vector_storage, Pinecone)
        mock_init.assert_called_once()
        mock_index.assert_called_once_with(index_name)

def test_qdrant_build_vector_storage():
    index_name = "index_name"
    embedding_model = MagicMock()

    with patch('superagi.vector_store.qdrant.create_qdrant_client') as mock_client:
        mock_client.return_value = MagicMock()
        vector_storage = VectorFactory.build_vector_storage(QDRANT, index_name, embedding_model, api_key='some_key', url='some_url', port='some_port')
        assert isinstance(vector_storage, Qdrant)
        mock_client.assert_called_once()

def test_unsupported_build_vector_store():
    with pytest.raises(ValueError):
        VectorFactory.build_vector_storage('unsupported', 'index_name', 'model')