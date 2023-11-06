import warnings
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Optional, Tuple

class VectorEmbeddings(ABC):

    @abstractmethod
    def get_vector_embeddings_from_chunks(
        self,
        final_chunks: Any
    ):
        """ Returns embeddings for vector dbs from final chunks"""