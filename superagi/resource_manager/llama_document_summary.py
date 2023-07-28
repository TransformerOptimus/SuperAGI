import os

from langchain.chat_models import ChatGooglePalm
from llama_index.indices.response import ResponseMode
from llama_index.schema import Document

from superagi.config.config import get_config
from superagi.lib.logger import logger
from superagi.types.model_source_types import ModelSourceType


class LlamaDocumentSummary:
    def __init__(self, model_name=get_config("RESOURCES_SUMMARY_MODEL_NAME", "gpt-3.5-turbo"), model_source="OpenAi", model_api_key: str = None):
        self.model_name = model_name
        self.model_api_key = model_api_key
        self.model_source = model_source

    def generate_summary_of_document(self, documents: list[Document]):
        """
        Generates summary of the documents

        :param documents: list of Document objects
        :return: summary of the documents
        """
        if documents is None or not documents:
            return
        from llama_index import LLMPredictor, ServiceContext, ResponseSynthesizer, DocumentSummaryIndex
        os.environ["OPENAI_API_KEY"] = get_config("OPENAI_API_KEY", "") or self.model_api_key
        llm_predictor_chatgpt = LLMPredictor(llm=self._build_llm())
        service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor_chatgpt, chunk_size=1024)
        response_synthesizer = ResponseSynthesizer.from_args(response_mode=ResponseMode.TREE_SUMMARIZE, use_async=True)
        doc_summary_index = DocumentSummaryIndex.from_documents(
            documents=documents,
            service_context=service_context,
            response_synthesizer=response_synthesizer
        )

        return doc_summary_index.get_document_summary(documents[0].doc_id)

    def generate_summary_of_texts(self, texts: list[str]):
        """
        Generates summary of the texts

        :param texts: list of texts
        :return: summary of the texts
        """
        from llama_index import Document
        if texts is not None and len(texts) > 0:
            documents = [Document(doc_id=f"doc_id_{i}", text=text) for i, text in enumerate(texts)]
            return self.generate_summary_of_document(documents)
        raise ValueError("texts must be provided")

    def _build_llm(self):
        """
        Builds the LLM model

        :return: LLM model object
        """
        open_ai_models = ['gpt-4', 'gpt-3.5-turbo', 'gpt-3.5-turbo-16k', 'gpt-4-32k']
        if self.model_name in open_ai_models:
            from langchain.chat_models import ChatOpenAI

            openai_api_key = get_config("OPENAI_API_KEY") or self.model_api_key
            return ChatOpenAI(temperature=0, model_name=self.model_name,
                              openai_api_key=openai_api_key)

        raise Exception(f"Model name {self.model_name} not supported for document summary")
