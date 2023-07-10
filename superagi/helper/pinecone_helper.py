from sqlalchemy.orm import Session
from superagi.models.vector_db_config import VectordbConfig
import pinecone

class PineconeHelper:
    
    def __init__(self, session):
        self.session = session
        
    def get_pinecone_client(self, vector_db):
        api_key = self.session.query(VectordbConfig).filter(VectordbConfig.vector_db_id == vector_db.id, VectordbConfig.key == "API_KEY").first()
        environment = self.session.query(VectordbConfig).filter(VectordbConfig.vector_db_id == vector_db.id, VectordbConfig.key == "ENVIRONMENT").first()
        pinecone.init(api_key=api_key.value, environment=environment.value)

    def get_dimensions(self,vector_db, vector_index):
        try:
            self.get_pinecone_client(vector_db)
            dimensions = pinecone.Index(vector_index.name).describe_index_stats().dimension
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

    def get_pinecone_index_state(self, vector_db, vector_index):
        try:
            self.get_pinecone_client(vector_db)
            total_vector_count = pinecone.Index(vector_index.name).describe_index_stats().total_vector_count
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