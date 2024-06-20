import json
import re
import uuid
from typing import Any, List, Iterable, Mapping
from typing import Optional, Pattern
import traceback
import numpy as np

from superagi.config.config import get_config
from superagi.lib.logger import logger
from superagi.vector_store.base import VectorStore
from superagi.vector_store.document import Document

DOC_PREFIX = "doc:"

CONTENT_KEY = "content"
METADATA_KEY = "metadata"
VECTOR_SCORE_KEY = "vector_score"


class MongoDB(VectorStore):

    def delete_embeddings_from_vector_db(self, ids: List[str]) -> None:
        pass

    def add_embeddings_to_vector_db(self, embeddings: dict) -> None:
        pass

    def get_index_stats(self) -> dict:
        pass

    DEFAULT_ESCAPED_CHARS = r"[,.<>{}\[\]\\\"\':;!@#$%^&*()\-+=~\/ ]"

    def __init__(self, index: Any, embedding_model: Any):
        """
        Args:
        index: An instance of a Redis index.
        embedding_model: An instance of a BaseEmbedding model.
        vector_group_id: vector group id used to index similar vectors.
        """
        self.index = index
        self.embedding_model = embedding_model
        self.content_key = "content",
        self.metadata_key = "metadata"
        self.index = index
        self.vector_key = "content_vector"

    def add_texts(self, texts: Iterable[str],
                  metadatas: Optional[List[dict]] = None,
                  embeddings: Optional[List[List[float]]] = None,
                  ids: Optional[list[str]] = None,
                  **kwargs: Any) -> List[str]:
        print('todo')

    def get_matching_text(self, query: str, top_k: int = 5, metadata: Optional[dict] = None, **kwargs: Any) -> List[Document]:
        return []
        
        

    def create_index(self):
        print('create_index')
