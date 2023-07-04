from unittest.mock import patch, Mock
from llama_index import VectorStoreIndex, StorageContext, Document
from superagi.resource_manager.resource_manager import ResourceManager
from superagi.resource_manager.llama_vector_store_factory import LlamaVectorStoreFactory


@patch.object(LlamaVectorStoreFactory, 'get_vector_store')
@patch.object(StorageContext, 'from_defaults')
@patch.object(VectorStoreIndex, 'from_documents')
def test_save_document_to_vector_store(mock_vc_from_docs, mock_sc_from_defaults, mock_get_vector_store):
    # Prepare test resources
    mock_vector_store = Mock()
    mock_get_vector_store.return_value = mock_vector_store
    mock_sc_from_defaults.return_value = "mock_storage_context"
    mock_vc_from_docs.return_value = "mock_index"

    resource_manager = ResourceManager("test_agent_id")
    documents = [Document(text="doc1"), Document(text="doc2")]
    resource_id = "test_resource_id"

    # Run test method
    resource_manager.save_document_to_vector_store(documents, resource_id, "test_model_api_key")

    # Validate calls
    mock_get_vector_store.assert_called_once()
    mock_sc_from_defaults.assert_called_once_with(vector_store=mock_vector_store)
    mock_vc_from_docs.assert_called_once_with(documents, storage_context="mock_storage_context")

    # Add more assertions here if needed, e.g., to check side effects
    mock_vector_store.persist.assert_called_once()