import pytest
from unittest.mock import patch, MagicMock
from superagi.types.vector_store_types import VectorStoreType
from superagi.vector_store.pinecone import Pinecone
from superagi.vector_store import weaviate
from superagi.vector_store.qdrant import Qdrant
from superagi.vector_store.vector_factory import VectorFactory

@patch('pinecone.init')
@patch('pinecone.list_indexes')
@patch('pinecone.Index')
@patch('pinecone.create_index')
@patch('weaviate.create_weaviate_client')
@patch('qdrant.create_qdrant_client')
def test_get_vector_storage(mock_create_qdrant, mock_create_weaviate, mock_create_index, mock_index, mock_list_indexes, mock_init):
    embedding_model = MagicMock()
    embedding_model.get_embedding.return_value = {'embedding1': 'value1'}

    mock_create_qdrant.return_value = MagicMock()
    mock_create_weaviate.return_value = MagicMock()
    mock_create_index.return_value = MagicMock()
    mock_index.return_value = MagicMock()
    mock_list_indexes.return_value = MagicMock()

    # test PINECONE
    result = VectorFactory.get_vector_storage(VectorStoreType.PINECONE, 'index1', embedding_model)
    assert isinstance(result, Pinecone)

    # test WEAVIATE
    result = VectorFactory.get_vector_storage(VectorStoreType.WEAVIATE, 'index1', embedding_model)
    assert isinstance(result, weaviate.Weaviate)

    # test QDRANT
    result = VectorFactory.get_vector_storage(VectorStoreType.QDRANT, 'index1', embedding_model)
    assert isinstance(result, Qdrant)
    
    # test not supported StoreType
    with pytest.raises(ValueError):
        VectorFactory.get_vector_storage('random', 'index1', embedding_model)
    

@patch('pinecone.init')
@patch('pinecone.Index')
@patch('qdrant.create_qdrant_client')
def test_build_vector_storage(mock_create_qdrant_client, mock_index_init, mock_pinecone_init):
    embedding_model = MagicMock()
    mock_create_qdrant_client.return_value = MagicMock()

    creds = {'api_key': 'api_key', 'environment': 'test', 'url': 'localhost', 'port': '8000'}

    # test for PINECONE
    result = VectorFactory.build_vector_storage(VectorStoreType.PINECONE, 'index2', embedding_model, **creds)
    assert isinstance(result, Pinecone)

    # test for QDRANT
    result = VectorFactory.build_vector_storage(VectorStoreType.QDRANT, 'index2', embedding_model, **creds)
    assert isinstance(result, Qdrant)