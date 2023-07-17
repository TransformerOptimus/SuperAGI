import uuid

from superagi.vector_store.document import Document
from superagi.vector_store.base import VectorStore
from typing import Any, Callable, Optional, Iterable, List

from superagi.vector_store.embedding.base import BaseEmbedding


class Pinecone(VectorStore):
    """
    Pinecone vector store.

    Attributes:
        index : The pinecone index.
        embedding_model : The embedding model.
        text_field : The text field is the name of the field where the corresponding text for an embedding is stored.
        namespace : The namespace.
    """
    def __init__(
            self,
            index: Any,
            embedding_model: Optional[Any],
            text_field: Optional[str],
            namespace: Optional[str] = '',
    ):
        try:
            import pinecone
        except ImportError:
            raise ValueError("Please install pinecone to use this vector store.")

        if not isinstance(index, pinecone.index.Index):
            raise ValueError("Please provide a valid pinecone index.")

        self.index = index
        self.embedding_model = embedding_model
        self.text_field = text_field
        self.namespace = namespace

    def add_texts(
            self,
            texts: Iterable[str],
            metadatas: Optional[list[dict]] = None,
            ids: Optional[list[str]] = None,
            namespace: Optional[str] = None,
            batch_size: int = 32,
            **kwargs: Any,
    ) -> list[str]:
        """
        Add texts to the vector store.

        Args:
            texts : The texts to add.
            metadatas : The metadatas to add.
            ids : The ids to add.
            namespace : The namespace to add.
            batch_size : The batch size to add.
            **kwargs : The keyword arguments to add.

        Returns:
            The list of ids vectors stored in pinecone.
        """
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

        self.index.upsert(vectors, namespace=namespace, batch_size=batch_size)
        return ids

    def get_matching_text(self, query: str, top_k: int = 5, metadata: Optional[dict] = {}, **kwargs: Any) -> List[Document]:
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
        filters = {}
        for key in metadata.keys():
            filters[key] = {"$eq": metadata[key]}
        embed_text = self.embedding_model.get_embedding(query)
        res = self.index.query(embed_text, filters=filters, top_k=top_k, namespace=namespace, include_metadata=True)

        documents = []

        for doc in res['matches']:
            documents.append(
                Document(
                    text_content=doc.metadata[self.text_field],
                    metadata=doc.metadata,
                )
            )

        return documents
    
    def get_index_stats(self) -> dict:
        """
        Returns:
            Stats or Information about an index
        """
        index_stats = self.index.describe_index_stats()
        dimensions = index_stats.dimensions
        vector_count = index_stats.total_vector_count
        
        return {"dimensions": dimensions, "vecttor_count": vector_count}
    
    def add_embeddings_to_vector_db(self, embeddings: dict) -> None:
        """Upserts embeddings to the given vector store"""
        try:
            self.index.upsert(vectors=embeddings["vectors"])
        except Exception as err:
            raise err
    
    def delete_embeddings_from_vector_db(self, ids: List[str]) -> None:
        """Deletes embeddings from the given vector store"""
        try:
            self.index.delete(ids=ids)
        except Exception as err:
            raise err