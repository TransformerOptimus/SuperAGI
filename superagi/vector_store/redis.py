import json
import re
import uuid
from typing import Any, List, Iterable, Mapping
from typing import Optional, Pattern
import traceback
import numpy as np
import redis
from redis.commands.search.field import TagField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType

from superagi.config.config import get_config
from superagi.lib.logger import logger
from superagi.vector_store.base import VectorStore
from superagi.vector_store.document import Document

DOC_PREFIX = "doc:"

CONTENT_KEY = "content"
METADATA_KEY = "metadata"
VECTOR_SCORE_KEY = "vector_score"


class Redis(VectorStore):

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
        redis_url = get_config('REDIS_URL')
        self.redis_client = redis.Redis.from_url("redis://" + redis_url + "/0", decode_responses=True)
        # self.redis_client = redis.Redis(host=redis_host, port=redis_port)
        self.index = index
        self.embedding_model = embedding_model
        self.content_key = "content",
        self.metadata_key = "metadata"
        self.index = index
        self.vector_key = "content_vector"

    def build_redis_key(self, prefix: str) -> str:
        """Build a redis key with a prefix."""
        return f"{prefix}:{uuid.uuid4().hex}"

    def add_texts(self, texts: Iterable[str],
                  metadatas: Optional[List[dict]] = None,
                  embeddings: Optional[List[List[float]]] = None,
                  ids: Optional[list[str]] = None,
                  **kwargs: Any) -> List[str]:
        pipe = self.redis_client.pipeline()
        prefix = DOC_PREFIX + str(self.index)
        keys = []
        for i, text in enumerate(texts):
            id = ids[i] if ids else self.build_redis_key(prefix)
            metadata = metadatas[i] if metadatas else {}
            embedding = self.embedding_model.get_embedding(text)
            embedding_arr = np.array(embedding, dtype=np.float32)

            pipe.hset(id, mapping={CONTENT_KEY: text, self.vector_key: embedding_arr.tobytes(),
                                   METADATA_KEY: json.dumps(metadata)})

            keys.append(id)
        pipe.execute()
        return keys

    def get_matching_text(self, query: str, top_k: int = 5, metadata: Optional[dict] = None, **kwargs: Any) -> List[Document]:
        
            embed_text = self.embedding_model.get_embedding(query)
            from redis.commands.search.query import Query
            hybrid_fields = self._convert_to_redis_filters(metadata)
            
            base_query = f"{hybrid_fields}=>[KNN {top_k} @{self.vector_key} $vector AS vector_score]"
            return_fields = [METADATA_KEY,CONTENT_KEY, "vector_score",'id']          
            query = (
                Query(base_query)
                .return_fields(*return_fields)
                .sort_by("vector_score")
                .paging(0, top_k)
                .dialect(2)
            )

            params_dict: Mapping[str, str] = {
                "vector": np.array(embed_text)
                .astype(dtype=np.float32)
                .tobytes()
            }

            # print(self.index)
            results = self.redis_client.ft(self.index).search(query,params_dict)
            
                # Prepare document results
            documents = []
            for result in results.docs:
                documents.append(
                    Document(
                        text_content=result.content,
                        metadata=json.loads(result.metadata)
                    )
                )
            return {"documents": documents}
        
        

    def _convert_to_redis_filters(self, metadata: Optional[dict] = None) -> str:
        if metadata is not None or len(metadata) == 0:
            return "*"
        filter_strings = []
        for key in metadata.keys():
            filter_string = "@%s:{%s}" % (key, self.escape_token(str(metadata[key])))
            filter_strings.append(filter_string)

        joined_filter_strings = " & ".join(filter_strings)
        return f"({joined_filter_strings})"

    def create_index(self):
        try:
            # check to see if index exists
            temp = self.redis_client.ft(self.index).info()
            logger.info(temp)
            logger.info("Index already exists!")
        except:
            vector_dimensions = self.embedding_model.get_embedding("sample")
            # schema
            schema = (
                TagField("tag"),  # Tag Field Name
                VectorField(self.vector_key,  # Vector Field Name
                            "FLAT", {  # Vector Index Type: FLAT or HNSW
                                "TYPE": "FLOAT32",  # FLOAT32 or FLOAT64
                                "DIM": len(vector_dimensions),  # Number of Vector Dimensions
                                "DISTANCE_METRIC": "COSINE",  # Vector Search Distance Metric
                            }
                            )
            )

            # index Definition
            definition = IndexDefinition(prefix=[DOC_PREFIX], index_type=IndexType.HASH)

            # create Index
            self.redis_client.ft(self.index).create_index(fields=schema, definition=definition)

    def escape_token(self, value: str) -> str:
        """
        Escape punctuation within an input string. Taken from RedisOM Python.

        Args:
            value (str): The input string.

        Returns:
            str: The escaped string.
        """
        escaped_chars_re = re.compile(Redis.DEFAULT_ESCAPED_CHARS)

        def escape_symbol(match: re.Match) -> str:
            return f"\\{match.group(0)}"

        return escaped_chars_re.sub(escape_symbol, value)