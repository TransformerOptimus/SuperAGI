import uuid

from superagi.vector_store.document import Document
from superagi.vector_store.base import VectorStore
from typing import Any, Callable, Optional, Iterable, List

from superagi.vector_store.embedding.openai import BaseEmbedding


class LanceDB(VectorStore):
    """
    LanceDB vector store.

    Attributes:
        tbl : The LanceDB table.
        embedding_model : The embedding model.
        text_field : The text field is the name of the field where the corresponding text for an embedding is stored.
        table_name : Name for the table in the vector database
    """
    def __init__(
            self,
            tbl: Any,
            embedding_model: BaseEmbedding,
            text_field: str,
            table_name : str,
    ):
        try:
            import lancedb
        except ImportError:
            raise ValueError("Please install LanceDB to use this vector store.")

        self.tbl = tbl
        self.embedding_model = embedding_model
        self.text_field = text_field
        self.table_name = table_name

    def add_texts(
            self,
            texts: Iterable[str],
            metadatas: Optional['list[dict]'] = None,
    ) -> 'list[str]':
        """
        Add texts to the vector store.

        Args:
            texts : The texts to add.
            fields: Additional fields to add.
        Returns:
            The list of ids vectors stored in LanceDB.
        """
        vectors = []
        ids = ids or [str(uuid.uuid4()) for _ in texts]
        if len(ids) < len(texts):
            raise ValueError("Number of ids must match number of texts.")

        for text, id in zip(texts, ids):
            metadata = metadatas.pop(0) if metadatas else {}
            metadata[self.text_field] = text
            vectors.append((id, self.embedding_model.get_embedding(text), metadata))

        self.tbl.add(vectors)
        return ids

    def get_matching_text(self, query: str, top_k: int = 5, **kwargs: Any) -> List[Document]:
        """
        Return docs most similar to query using specified search type.

        Args:
            query : The query to search.
            top_k : The top k to search.
            **kwargs : The keyword arguments to search.

        Returns:
            The list of documents most similar to the query
        """
        namespace = kwargs.get("namespace", self.namespace)

        embed_text = self.embedding_model.get_embedding(query)
        res = self.tbl.search(embed_text).limit(top_k).to_df()

        documents = []

        for doc in res['matches']:
            documents.append(
                Document(
                    text_content=doc.metadata[self.text_field],
                    metadata=doc.metadata,
                )
            )

        return documents

