import pytest
from unittest.mock import patch
from superagi.resource_manager.llama_document_summary import LlamaDocumentSummary
from llama_index.schema import Document

class MockLLMPredictor:
    # This mock class will replace LLMPredictor
    def __init__(self, llm):
        pass

class MockServiceContext:
    # This mock class will replace ServiceContext
    @classmethod
    def from_defaults(cls, llm_predictor, chunk_size):
        pass

class MockResponseSynthesizer:
    # This mock class will replace ResponseSynthesizer
    @classmethod
    def from_args(cls, response_mode, use_async):
        pass

class MockDocumentSummaryIndex:
    # This mock class will handle DocumentSummaryIndex
    @classmethod
    def from_documents(cls, documents, service_context, response_synthesizer):
        return cls()

    def get_document_summary(cls, doc_id):
        return f'This is a summary of the document with id: {doc_id}'


@patch('llama_index.LLMPredictor', MockLLMPredictor)
@patch('llama_index.ServiceContext', MockServiceContext)
@patch('llama_index.ResponseSynthesizer', MockResponseSynthesizer)
@patch('llama_index.DocumentSummaryIndex', MockDocumentSummaryIndex)
def test_generate_summary_of_documents():
    lds = LlamaDocumentSummary()
    # Documents to be summarized
    documents = [
        Document(doc_id='1', text='The quick brown fox jumps over the lazy dog'),
        Document(doc_id='2', text='Hello World!')
    ]
    # Generate summary
    summary = lds.generate_summary_of_document(documents)
    # Ensure mock summary is returned
    assert summary == 'This is a summary of the document with id: 1'

@patch('llama_index.LLMPredictor', MockLLMPredictor)
@patch('llama_index.ServiceContext', MockServiceContext)
@patch('llama_index.ResponseSynthesizer', MockResponseSynthesizer)
@patch('llama_index.DocumentSummaryIndex', MockDocumentSummaryIndex)
def test_generate_summary_of_documents_from_texts():
    lds = LlamaDocumentSummary()
    # Documents to be summarized
    texts = [
        'The quick brown fox jumps over the lazy dog',
        'Hello World!'
    ]
    # Generate summary
    summary = lds.generate_summary_of_texts(texts)
    # Ensure mock summary is returned
    assert summary == 'This is a summary of the document with id: doc_id_0'

    texts = []
    # Generate summary
    with pytest.raises(Exception) as excinfo:
        lds.generate_summary_of_texts(texts)
    assert "texts must be provided" in str(excinfo.value)