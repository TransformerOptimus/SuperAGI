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
    def get_matching_text(self, query: str, top_k: int, **kwargs: Any) -> List[Document]:
        """Return docs most similar to query using specified search type."""

    def add_documents(self, documents: List[Document], **kwargs: Any) -> List[str]:
        """Run more documents through the embeddings and add to the vectorstore.
        """
        texts = [doc.text_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        return self.add_texts(texts, metadatas, **kwargs)
    
    @abstractmethod
    def get_index_dimensions(self) -> int:
        """Returns dimensions of an index"""

    @abstractmethod
    def get_index_vector_count(self) -> int:
        """Returns vector count of an index"""
