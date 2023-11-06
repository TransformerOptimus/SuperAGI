from __future__ import annotations

from abc import abstractmethod
from typing import Any, Dict, Iterable, List, Optional, Tuple

import weaviate
from uuid import uuid4
from superagi.vector_store.base import VectorStore
from superagi.vector_store.document import Document


def create_weaviate_client(
    url: Optional[str] = None,
    api_key: Optional[str] = None,
) -> weaviate.Client:
    """
    Creates a Weaviate client instance.

    Args:
        use_embedded: Whether to use the embedded Weaviate instance. Defaults to True.
        url: The URL of the Weaviate instance to connect to. Required if `use_embedded` is False.
        api_key: The API key to use for authentication if using Weaviate Cloud Services. Optional.

    Returns:
        A Weaviate client instance.

    Raises:
        ValueError: If invalid argument combination are passed.
    """
    if url:
        if api_key:
            auth_config = weaviate.AuthApiKey(api_key=api_key)
        else:
            auth_config = None

        client = weaviate.Client(url=url, auth_client_secret=auth_config)
    else:
        raise ValueError("Invalid arguments passed to create_weaviate_client")

    return client


class Weaviate(VectorStore):
    def __init__(
        self, client: weaviate.Client, embedding_model: Any, class_name: str, text_field: str = "text"
    ):
        self.class_name = class_name
        self.embedding_model = embedding_model
        self.text_field = text_field

        self.client = client

    def add_texts(
        self, texts: Iterable[str], metadatas: List[dict] | None = None, **kwargs: Any
    ) -> List[str]:
        result = {}
        collected_ids = []
        for i, text in enumerate(texts):
            metadata = metadatas[i] if metadatas else {}
            data_object = metadata.copy()
            data_object[self.text_field] = text
            vector = self.embedding_model.get_embedding(text)
            id = str(uuid4())
            result = {"ids": id, "data_object": data_object, "vectors": vector}
            collected_ids.append(id)
            self.add_embeddings_to_vector_db(result)
        return collected_ids

    def get_matching_text(
        self, query: str, top_k: int = 5, metadata: dict = None, **kwargs: Any
    ) -> List[Document]:
        metadata_fields = self._get_metadata_fields()
        query_vector = self.embedding_model.get_embedding(query)
        if metadata is not None:
            for key, value in metadata.items():
                filters = {
                    "path": [key],
                    "operator": "Equal",
                    "valueString": value
                }

        results = self.client.query.get(
            self.class_name,
            metadata_fields + [self.text_field],
        ).with_near_vector(
            {"vector": query_vector, "certainty": 0.7}
        ).with_where(filters).with_limit(top_k).do()

        results_data = results["data"]["Get"][self.class_name]
        search_res = self._get_search_res(results_data, query)
        documents = self._build_documents(results_data, metadata_fields)

        return {"search_res": search_res, "documents": documents}
    
    def _get_metadata_fields(self) -> List[str]:
        schema = self.client.schema.get(self.class_name)
        property_names = []
        for property_schema in schema["properties"]:
            property_names.append(property_schema["name"])

        property_names.remove(self.text_field)
        return property_names

    def get_index_stats(self) -> dict:
        result = self.client.query.aggregate(self.class_name).with_meta_count().do()
        vector_count = result['data']['Aggregate'][self.class_name][0]['meta']['count']
        return {'vector_count': vector_count}

    def add_embeddings_to_vector_db(self, embeddings: dict) -> None:
        try:
            with self.client.batch as batch:
                for i in range(len(embeddings['ids'])):
                    data_object = {key: value for key, value in embeddings['data_object'][i].items()}
                    batch.add_data_object(data_object, class_name=self.class_name, uuid=embeddings['ids'][i], vector=embeddings['vectors'][i])
        except Exception as err:
            raise err
        
    def delete_embeddings_from_vector_db(self, ids: List[str]) -> None:
        try:
            for id in ids:
                self.client.data_object.delete(
                    uuid = id,
                    class_name = self.class_name
                )
        except Exception as err:
            raise err
    
    def _build_documents(self, results_data, metadata_fields) -> List[Document]:
        documents = []
        for result in results_data:
            text_content = result[self.text_field]
            metadata = {}
            for field in metadata_fields:
                metadata[field] = result[field]
            document = Document(text_content=text_content, metadata=metadata)
            documents.append(document)
        
        return documents
    
    def _get_search_res(self, results, query):
        text = [item['text'] for item in results]
        search_res = f"Query: {query}\n"
        i = 0
        for context in text:
            search_res += f"Chunk{i}: \n{context}\n"
            i += 1
        return search_res