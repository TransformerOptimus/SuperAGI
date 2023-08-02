import warnings
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Optional, Tuple
from superagi.vector_store.document import Document


class VectorStore(ABC):
    @abstractmethod
    def add_texts(
            self,
            texts: Iterable[str],
            metadatas: Optional[List[dict]] = None,
            **kwargs: Any,
    ) -> List[str]:
        """Add texts to the vector store."""

    @abstractmethod
    def get_matching_text(self, query: str, top_k: int, metadata: Optional[dict], **kwargs: Any) -> List[Document]:
        """Return docs most similar to query using specified search type."""

    def add_documents(self, documents: List[Document], **kwargs: Any) -> List[str]:
        """Run more documents through the embeddings and add to the vectorstore.
        """
        texts = [doc.text_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        return self.add_texts(texts, metadatas, **kwargs)
    
    @abstractmethod
    def get_index_stats(self) -> dict:
        """Returns stats or information of an index"""
    
    @abstractmethod
    def add_embeddings_to_vector_db(self, embeddings: dict) -> None:
        """Add embeddings to the vector store."""
    
    @abstractmethod
    def delete_embeddings_from_vector_db(self,ids: List[str]) -> None:
        """Delete embeddings from the vector store."""