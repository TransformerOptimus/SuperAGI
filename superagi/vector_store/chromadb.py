

import uuid
from typing import Any, Callable, Optional, Iterable, List

from superagi.vector_store.document import Document
from superagi.vector_store.base import VectorStore
from superagi.vector_store.embedding.openai import BaseEmbedding
from superagi.chromadb.client import ChromaDBClient


class ChromaDB(VectorStore):
    def __init__(
        self,
        client: ChromaDBClient,
        embedding_model: BaseEmbedding,
        text_field: str,
        namespace: Optional[str] = "",
    ):
        self.client = client
        self.embedding_model = embedding_model
        self.text_field = text_field
        self.namespace = namespace

    def add_texts(
        self,
        texts: Iterable[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None,
        namespace: Optional[str] = None,
        batch_size: int = 32,
        **kwargs: Any,
    ) -> List[str]:
        """Add texts to the vector store."""
        if namespace is None:
            namespace = self.namespace

        vectors = []
        ids = ids or [str(uuid.uuid4()) for _ in texts]
        if len(ids) < len(texts):
            raise ValueError("Number of ids must match number of texts.")

        for text, id in zip(texts, ids):
            metadata = metadatas.pop(0) if metadatas else {}
            metadata[self.text_field] = text
            vectors.append((id, self.embedding_model.get_embedding(text), metadata))

        self.client.set_items(vectors, namespace=namespace)
        return ids

    def get_matching_text(self, query: str, top_k: int = 5, **kwargs: Any) -> List[Document]:
        """Return docs most similar to query using specified search type."""
        namespace = kwargs.get("namespace", self.namespace)

        embed_text = self.embedding_model.get_embedding(query)
        res = self.client.query_by_embedding(embed_text, top_k=top_k, namespace=namespace)

        documents = []

        for doc in res:
            metadata = doc.get("metadata", {})
            documents.append(
                Document(
                    text_content=metadata[self.text_field],
                    metadata=metadata,
                )
            )

        return documents

