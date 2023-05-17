import warnings
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Optional, Tuple
from document import Document


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
    def get_matching_text(self, query: str, **kwargs: Any) -> List[Document]:
        """Return docs most similar to query using specified search type."""
