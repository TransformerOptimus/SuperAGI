from unittest.mock import MagicMock, patch
import numpy as np
from superagi.vector_store.document import Document
from superagi.vector_store.redis import Redis


def test_escape_token():
    redis_object = Redis(None, None)
    escaped_token = redis_object.escape_token("An,example.<> string!")
    assert escaped_token == "An\\,example\\.\\<\\>\\ string\\!"

@patch('redis.Redis')
def test_add_texts(redis_mock):
    # Arrange
    mock_index = "mock_index"
    mock_embedding_model = MagicMock()
    redis_object = Redis(mock_index, mock_embedding_model)
    redis_object.build_redis_key = MagicMock(return_value="mock_key")
    texts = ["Hello", "World"]
    metadatas = [{"data": 1}, {"data": 2}]

    # Act
    redis_object.add_texts(texts, metadatas)

    # Assert
    assert redis_object.redis_client.pipeline().hset.call_count == len(texts)

@patch('redis.Redis')
def test_get_matching_text(redis_mock):
    # Arrange
    mock_index = "mock_index"
    redis_object = Redis(mock_index, None)
    redis_object.embedding_model = MagicMock()
    redis_object.embedding_model.get_embedding.return_value = np.array([0.1, 0.2, 0.3])
    query = "mock_query"

    # Act
    result = redis_object.get_matching_text(query, metadata={})

    # Assert
    redis_object.embedding_model.get_embedding.assert_called_once_with(query)
    assert "documents" in result