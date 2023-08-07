from typing import Any, Iterable, List, Optional
from superagi.vector_store.document import Document
from superagi.vector_store.base import VectorStore
from superagi.vector_store.embedding.openai import BaseEmbedding


class Milvus(VectorStore):
    def __init__(
        self,
        embedding_model: BaseEmbedding,
        dim=1536,
        uri="http://localhost:19530",
        token=None,
        collection_name="SuperAgi",
        overwrite=False,
    ):
        """Create a Milvus Vector Store

        Args:
            embedding_model (BaseEmbedding): Embedding model to use for embedding text.
            dim (int, optional): The dimension of the embedding function results. Defaults to 1536.
            uri (str, optional): Uri to connect to cluster. Defaults to "http://localhost:19530".
            token (_type_, optional): Token if applicable for cluster. Defaults to None.
            collection_name (str, optional): What to name the collection. Defaults to "SuperAgi".
            overwrite (bool, optional): Overwrite previous collection with same 
                name. Defaults to False.

        Raises:
            ValueError: Error importing pymilvus.
        """
        try:
            from pymilvus import MilvusClient
        except ImportError as error:
            raise ValueError("Please install pymilvus to use this vector store.") from error

        self.model = embedding_model
        self.collection_name = collection_name
        self.client = MilvusClient(uri=uri, token=token)
        if collection_name in self.client.list_collections():
            if overwrite:
                self.client.drop_collection(collection_name=collection_name)
                self.client.create_collection(
                    collection_name=collection_name,
                    dimension=dim,
                    auto_id=True,
                    consistency_level="Session"
                )
        else:
            self.client.create_collection(
                collection_name=collection_name,
                dimension=dim,
                auto_id=True,
                consistency_level="Session"
            )

    def add_texts(
        self,
        texts: Iterable[str],
        metadatas: Optional[List[dict]] = None,
        batch_size=100,
        **kwargs: Any,
    ) -> List[str]:
        """Add texts to the vector store."""
        inserts = []
        for text, metadata in zip(texts, metadatas):
            idict = {}
            idict["vector"] = self.model.get_embedding(text)
            idict["text"] = text
            if not (metadata is None or len(metadata) == 0):
                idict["metadata"] = metadata
            inserts.append(idict)

        self.client.insert(collection_name=self.collection_name, data=inserts, batch_size=batch_size)

    def get_matching_text(
        self, query: str, top_k: int, **kwargs: Any
    ) -> List[Document]:
        """Return docs most similar to query using specified search type."""
        result = self.client.search(
            collection_name=self.collection_name,
            data=[self.model.get_embedding(query)],
            limit=top_k,
            output_fields=["*"]
        )
        docs = []
        for hit in result[0]:
            docs.append(
                Document(
                    text_content=hit["entity"]["text"],
                    metadata=hit["entity"].get("metadata", {}),
                )
            )
        return docs


    def add_documents(self, documents: List[Document], **kwargs: Any) -> List[str]:
        """Run more documents through the embeddings and add to the vectorstore."""
        texts = [doc.text_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        return self.add_texts(texts, metadatas, **kwargs)
 