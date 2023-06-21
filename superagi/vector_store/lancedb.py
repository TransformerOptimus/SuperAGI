import uuid

from superagi.vector_store.document import Document
from superagi.vector_store.base import VectorStore
from typing import Any, Callable, Optional, Iterable, List

from superagi.vector_store.embedding.openai import BaseEmbedding


class LanceDB(VectorStore):
    """
    LanceDB vector store.

    Attributes:
        db : The LanceDB connected database.
        embedding_model : The embedding model.
        text_field : The text field is the name of the field where the corresponding text for an embedding is stored.
        table_name : Name for the table in the vector database
    """
    def __init__(
            self,
            db: Any,
            embedding_model: BaseEmbedding,
            text_field: str,
    ):
        try:
            import lancedb
        except ImportError:
            raise ValueError("Please install LanceDB to use this vector store.")

        self.db = db
        self.embedding_model = embedding_model
        self.text_field = text_field

    def add_texts(
            self,
            texts: Iterable[str],
            metadatas: Optional['list[dict]'] = None,
            ids: Optional['list[str]'] = None,
            table_name: Optional[str] = None,
    ) -> 'list[str]':
        """
        Add texts to the vector store.

        Args:
            texts : The texts to add.
            metadatas: The metadatas to add.
            ids : The ids to add.
            table_name : The table to add.
        Returns:
            The list of ids vectors stored in LanceDB.
        """

        vectors = []
        ids = ids or [str(uuid.uuid4()) for _ in texts]
        if len(ids) < len(texts):
            raise ValueError("Number of ids must match number of texts.")

        for text, id in zip(texts, ids):
            vector = {}
            metadata = metadatas.pop(0) if metadatas else {}
            metadata[self.text_field] = text

            vector["id"] = id
            vector["vector"] = self.embedding_model.get_embedding(text)
            for key, value in metadata.items():
                vector[key] = value

            vectors.append(vector)

        try:
            tbl = self.db.create_table(table_name, data=vectors)
        except:
            tbl = self.db.open_table(table_name)
            tbl.add(vectors)

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

        try:
            tbl = self.db.open_table(namespace)
        except:
            raise ValueError("Table name was not found in LanceDB")

        embed_text = self.embedding_model.get_embedding(query)
        res = tbl.search(embed_text).limit(top_k).to_df()

        documents = []

        for i in range(len(res)):
            meta = {}
            for col in res:
                if col != 'vector' and col != 'id':
                    meta[col] = res[col][i]

            documents.append(
                Document(
                    text_content=res[self.text_field][i],
                    metadata=meta,
                )
            )

        return documents
