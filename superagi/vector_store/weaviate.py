from __future__ import annotations

from abc import abstractmethod
from typing import Any, Dict, Iterable, List, Optional, Tuple

import weaviate

from superagi.vector_store.base import VectorStore
from superagi.vector_store.document import Document


def create_weaviate_client(
    use_embedded: bool = True,
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
    if use_embedded:
        client = weaviate.Client(embedded_options=weaviate.embedded.EmbeddedOptions())
    elif url:
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
        self, client: weaviate.Client, embedding_model: Any, index: str, text_field: str
    ):
        self.index = index
        self.embedding_model = embedding_model
        self.text_field = text_field

        self.client = client

    def add_texts(
        self, texts: Iterable[str], metadatas: List[dict] | None = None, **kwargs: Any
    ) -> List[str]:
        result = []
        with self.client.batch as batch:
            for i, text in enumerate(texts):
                metadata = metadatas[i] if metadatas else {}
                data_object = metadata.copy()
                data_object[self.text_field] = text
                vector = self.embedding_model.get_embedding(text)

                batch.add_data_object(data_object, class_name=self.index, vector=vector)

                object = batch.create_objects()[0]
                result.append(object["id"])
        return result

    def get_matching_text(
        self, query: str, top_k: int = 5, **kwargs: Any
    ) -> List[Document]:
        alpha = kwargs.get("alpha", 0.5)
        metadata_fields = self._get_metadata_fields()
        query_vector = self.embedding_model.get_embedding(query)

        results = (
            self.client.query.get(self.index, metadata_fields + [self.text_field])
            .with_hybrid(query, vector=query_vector, alpha=alpha)
            .with_limit(top_k)
            .do()
        )

        results_data = results["data"]["Get"][self.index]
        documents = []
        for result in results_data:
            text_content = result[self.text_field]
            metadata = {}
            for field in metadata_fields:
                metadata[field] = result[field]
            document = Document(text_content=text_content, metadata=metadata)
            documents.append(document)

        return documents

    def _get_metadata_fields(self) -> List[str]:
        schema = self.client.schema.get(self.index)
        property_names = []
        for property_schema in schema["properties"]:
            property_names.append(property_schema["name"])

        property_names.remove(self.text_field)
        return property_names
