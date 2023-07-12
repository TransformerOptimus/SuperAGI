from sqlalchemy.orm import Session
from superagi.models.vector_db_config import VectordbConfig
import pinecone

class PineconeHelper:
    
    def __init__(self, session):
        self.session = session

    def get_dimensions(self, api_key, environment, index_name):
        try:
            pinecone.init(api_key=api_key, environment=environment)
            dimensions = pinecone.Index(index_name).describe_index_stats().dimension
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

    def get_pinecone_index_state(self, api_key, environment, index_name):
        try:
            pinecone.init(api_key=api_key, environment=environment)
            total_vector_count = pinecone.Index(index_name).describe_index_stats().total_vector_count
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