import uuid

from superagi.vector_store.document import Document
from superagi.vector_store.base import VectorStore
from typing import Any, Callable, Optional, Iterable, List

from superagi.vector_store.embedding.openai import BaseEmbedding


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
            embedding_model: BaseEmbedding,
            text_field: str,
            namespace: Optional[str] = '',
            vector_group_id: Optional[str] = None):
        """
            Create a vector store using Pinecone.
            Args:
            index: An instance of a Pinecone index.
            embedding_model: An instance of a BaseEmbedding model.
            text_field: The name of the field in the metadata that contains the text.
            namespace: The namespace to use for the Pinecone index.
            vector_group_id: Vector group id used to index similar vectors.
        """
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
        self.vector_group_id = vector_group_id

    @classmethod
    def create_index(cls, index_name, embedding_model):
        """Create a Pinecone index.
        Args:
        index_name: The name of the index to create.
        embedding_model: An instance of a BaseEmbedding model.
        """
        try:
            import pinecone
        except ImportError:
            raise ValueError("Please install pinecone to use this vector store.")
        if index_name not in pinecone.list_indexes():
            sample_embedding = embedding_model.get_embedding("sample")

            # if does not exist, create index
            pinecone.create_index(
                index_name,
                dimension=len(sample_embedding),
                metric='dotproduct'
            )
        index = pinecone.Index(index_name)
        return index

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
            metadata = metadatas.pop() if metadatas else {}
            metadata[self.text_field] = text
            metadata["vector_group_id"] = self.vector_group_id
            vectors.append((id, self.embedding_model.get_embedding(text), metadata))

        self.index.upsert(vectors, namespace=namespace, batch_size=batch_size)
        return ids

    def get_matching_text(self, query: str, top_k: int = 5, metadata: Optional[dict] = None, **kwargs: Any) -> List[
        Document]:
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

        filter = {
            "vector_group_id": {"$eq": self.vector_group_id}
        } if self.vector_group_id else None

        embed_text = self.embedding_model.get_embedding(query)
        res = self.index.query(embed_text, filter=filter, top_k=top_k, namespace=namespace, include_metadata=True)

        documents = []

        for doc in res['matches']:
            documents.append(
                Document(
                    text_content=doc.metadata[self.text_field],
                    metadata=doc.metadata,
                )
            )
        return documents
