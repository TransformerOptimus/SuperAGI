import pytest
from unittest.mock import MagicMock, patch
from superagi.vector_store.chromadb import ChromaDB
from superagi.vector_store.document import Document
from superagi.vector_store.embedding.openai import OpenAiEmbedding
from superagi.vector_store.embedding.base import BaseEmbedding

@pytest.fixture
def mock_embedding_model():
    mock_model = MagicMock(spec=BaseEmbedding)
    mock_model.get_embedding.return_value = [0.1, 0.2, 0.3]  # dummy embedding vector
    return mock_model

@patch('chromadb.Client')
def test_create_collection(mock_chromadb_client):
    ChromaDB.create_collection('test_collection')
    mock_chromadb_client().get_or_create_collection.assert_called_once_with(name='test_collection')

@patch('chromadb.Client')
def test_add_texts(mock_chromadb_client, mock_embedding_model):
    chroma_db = ChromaDB('test_collection', mock_embedding_model, 'text')
    chroma_db.add_texts(['hello world'], [{'key': 'value'}])
    mock_chromadb_client().get_collection().add.assert_called_once()

@patch('chromadb.Client')
@patch.object(BaseEmbedding, 'get_embedding')
def test_get_matching_text(mock_get_embedding, mock_chromadb_client):
    # Setup
    mock_get_embedding.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]  # dummy vector

    mock_chromadb_client().get_collection().query.return_value = {
        'ids': [['id1', 'id2', 'id3']],
        'documents': [['doc1', 'doc2', 'doc3']],
        'metadatas': [[{'meta1': 'value1'}, {'meta2': 'value2'}, {'meta3': 'value3'}]]
    }
    chroma_db = ChromaDB('test_collection', OpenAiEmbedding(api_key="asas"), 'text')

    # Execute
    documents = chroma_db.get_matching_text('hello world')

    # Validate
    assert isinstance(documents[0], Document)
    assert len(documents) == 3
    for doc in documents:
        assert 'text_content' in doc.dict().keys()
        assert 'metadata' in doc.dict().keys()