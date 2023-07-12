from sqlalchemy.orm import Session
from superagi.models.vector_db_config import VectordbConfig
from qdrant_client import models, QdrantClient

class QdrantHelper:
    
    def __init__(self, session, vector_db):
        self.session = session
    
    def get_dimensions(self, api_key, url, port, vector_index):
        try:
            qdrant_client = QdrantClient(
                api_key=api_key,
                url=url
            )
            collection_info = qdrant_client.get_collection(collection_name=vector_index.name)
            dimensions = collection_info.config.params.vectors.size
            data = {
                "success": True,
                "dimensions": str(dimensions)
            }
        except:
            data = {
                "success": False,
                "message": "Failed to Connect"
            }
        return data
    
    def get_qdrant_index_state(self, api_key, url, port, vector_index):
        try:
            qdrant_client = QdrantClient(
                api_key=api_key,
                url=url
            )
            collection_info = qdrant_client.get_collection(collection_name=vector_index.name)
            total_vector_count = collection_info.vectors_count
            if total_vector_count > 0:
                state = "CUSTOM"
            else:
                state = "NONE"
            data = {
                "success": True,
                "state": state
            }
        except:
            data = {
                "success": False,
                "message": "Failed to Connect"
            }
        return data