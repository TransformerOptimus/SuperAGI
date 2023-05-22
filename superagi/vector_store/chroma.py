import uuid
import os


from superagi.vector_store.document import Document
from superagi.vector_store.base import VectorStore
from typing import Any, Callable, Optional, Iterable, List, Dict
from pathlib import Path


class ChromaDB(VectorStore):

    def __init__(
            self,
            collection_name: str = 'default',
            embedding_function: Callable = None,
            persist_directory: Optional[str] = None,
            client_settings: Any = None,
            collection_metadata: Optional[Dict] = None,
            client: Any = None,
    ) -> None:

        try:
            import chromadb
            import chromadb.config
        except ImportError:
            raise ValueError(
                "Please install chromadb to use this vector store: pip install chromadb"
            )
        if persist_directory is None:
            persist_directory = os.path.dirname(Path(__file__).parent.parent) + "/chromadb_data/"
            print(persist_directory, "persist_directory")
        if client:
            self.client = client
        else:
            if client_settings:
                self.client_settings = client_settings
            else:
                self.client_settings = chromadb.config.Settings()
                if persist_directory:
                    self.client_settings = chromadb.config.Settings(
                        chroma_db_impl="duckdb+parquet",
                        persist_directory=persist_directory,
                    )
            self.client = chromadb.Client(self.client_settings)

        self.collection_name = collection_name
        self.collection_metadata = collection_metadata
        self.embedding_function = embedding_function
        self.collection = self.client.get_or_create_collection(name=self.collection_name,
                                                               metadata=self.collection_metadata,
                                                               embedding_function=self.embedding_function)

    def get_matching_text(self, query: str, top_k: int = 5, **kwargs: Any) -> List[Document]:
        """Return docs most similar to query using specified search type."""
        query_embeddings = self.embedding_function.get_embedding(query)
        try:
            import chromadb
        except ImportError:
            raise ValueError("Please install chromadb to use this vector store.")
        for i in range(top_k, 0, -1):
            try:
                result = self.collection.query(
                    query_embeddings=query_embeddings,
                    n_results=i,
                )
                break
            except chromadb.errors.NotEnoughElementsException:
                continue
        print(result, "result")
        temp = zip(result.get('metadatas')[0], result.get('distances')[0], result.get('documents')[0])
        print(temp, "temp")
        documents = []
        for doc in temp:
            documents.append(
                Document(
                    text_content=doc[2],
                    metadata=doc[0],
                )
            )
        return documents

    def add_texts(
            self,
            texts: Iterable[str],
            metadatas: Optional[list[dict]] = None,
            ids: Optional[list[str]] = None,
            **kwargs: Any,
    ) -> list[str]:
        ids = ids or [str(uuid.uuid4()) for _ in texts]
        embeddings = None
        if self.embedding_function is not None:
            embeddings = self.embedding_function.embed_documents(list(texts))
        self.collection.add(
            metadatas=metadatas, embeddings=embeddings, documents=texts, ids=ids
        )
        return ids
