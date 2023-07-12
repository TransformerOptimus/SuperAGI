from __future__ import annotations

import uuid
from mimetypes import common_types
from typing import Any, Dict, Iterable, List, Optional, Tuple, Sequence, Union

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.conversions import common_types

from superagi.vector_store.base import VectorStore
from superagi.vector_store.document import Document

DictFilter = Dict[str, Union[str, int, bool, dict, list]]
MetadataFilter = Union[DictFilter, common_types.Filter]

def create_qdrant_client(
) -> QdrantClient:
    client = QdrantClient(host="localhost", port=6333)
    return client

class Qdrant(VectorStore):
    TEXT_FIELD_KEY = "text_field"
    METADATA_KEY = "metadata"

    def __init__(
        self,
        client: QdrantClient,
        embedding_model: Any,
        collection_name: str
        ,text_field_payload_key: str = TEXT_FIELD_KEY,
        metadata_payload_key: str = METADATA_KEY,
    ):
        self.client = client
        self.embedding_model = embedding_model
        self.collection_name = collection_name
        self.text_field_payload_key = text_field_payload_key or self.TEXT_FIELD_KEY
        self.metadata_payload_key = metadata_payload_key or self.METADATA_KEY

    def add_texts(
            self,
            input_texts: Iterable[str],
            metadata_list: Optional[List[dict]] = None,
            id_list: Optional[Sequence[str]] = None,
            batch_limit: int = 64,
    ) -> List[str]:

        collected_ids = []
        metadata_list = metadata_list or []
        id_list = id_list or [uuid.uuid4().hex for _ in input_texts]
        num_batches = len(input_texts) // batch_limit + (len(input_texts) % batch_limit != 0)

        for i in range(num_batches):
            text_batch = input_texts[i * batch_limit: (i + 1) * batch_limit]
            metadata_batch = metadata_list[i * batch_limit: (i + 1) * batch_limit] or None
            id_batch = id_list[i * batch_limit: (i + 1) * batch_limit]

            self.client.upsert(
                collection_name=self.collection_name,
                points=models.Batch.construct(
                    ids=id_batch,
                    vectors=self.__get_embeddings(text_batch),
                    payloads=self.__build_payloads(
                        text_batch,
                        metadata_batch,
                        self.text_field_payload_key,
                        self.metadata_payload_key,
                    ),
                ),
            )

            collected_ids.extend(id_batch)

        return collected_ids

    def get_matching_text(
            self,
            embedding: List[float] = None,
            k: int = 4,
            text: str = None,
            filter: Optional[MetadataFilter] = None,
            search_params: Optional[common_types.SearchParams] = None,
            offset: int = 0,
            score_threshold: Optional[float] = None,
            consistency: Optional[common_types.ReadConsistency] = None,
            **kwargs: Any,
    ) -> List[Tuple[Document, float]]:
        if embedding is not None and text is not None:
            raise ValueError("Only provide embedding or text")
        if text is not None:
            embedding = self.__get_embeddings(text)[0]

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=embedding,
            query_filter=filter,
            search_params=search_params,
            limit=k,
            offset=offset,
            with_payload=True,
            with_vectors=False,
            score_threshold=score_threshold,
            consistency=consistency,
            **kwargs,
        )

        return self.__build_documents(results)

    def __get_embeddings(
            self,
            texts: Iterable[str]
    ) -> List[List[float]]:
        if self.embedding_model is not None:
            query_vectors = []
            for text in texts:
                query_vector = self.embedding_model.get_embedding(text)
                query_vectors.append(query_vector)
        else:
            raise ValueError("Embedding model is not set")

        return query_vectors

    def __build_payloads(
            self,
            texts: Iterable[str],
            metadatas: Optional[List[dict]],
            text_field_payload_key: str,
            metadata_payload_key: str,
    ) -> List[dict]:
        payloads = []
        for i, text in enumerate(texts):
            if text is None:
                raise ValueError(
                    "One or more of the text entries is set to None. "
                    "Ensure to eliminate these before invoking the .add_texts method on the Qdrant instance."
                )
            metadata = metadatas[i] if metadatas is not None else None
            payloads.append(
                {
                    text_field_payload_key: text,
                    metadata_payload_key: metadata,
                }
            )

        return payloads

    def __build_documents(
            self,
            results: List[Dict]
    ) -> List[Document]:
        documents = []
        for result in results:
            documents.append(
                Document(
                    text_content=result.payload.get(self.text_field_payload_key),
                    metadata=result.payload.get(self.metadata_payload_key) or {},
                )
            )

        return documents