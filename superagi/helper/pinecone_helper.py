from sqlalchemy.orm import Session
from superagi.models.vector_db_config import VectordbConfig
import pinecone

class PineconeHelper:
    
    def __init__(self, session, api_key, environment):
        self.session = session
        self.api_key = api_key
        self.environment = environment

    def get_dimensions(self,index_name):
        try:
            pinecone.init(api_key=self.api_key, environment=self.environment)
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

    def get_pinecone_index_state(self, index_name):
        try:
            pinecone.init(api_key=self.api_key, environment=self.environment)
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
    
    def get_upsert_data(self, chunk_json):
        final_chunks = []
        for key in chunk_json.keys():
            final_chunks.append(chunk_json[key])
        
        uuid =[]
        embeds = []
        metadata = []
        for i in range(0, len(final_chunks)):
            uuid.append(final_chunks[i]["id"])
            embeds.append(final_chunks[i]["embeds"])
            data = {
                'text': final_chunks[i]['text'],
                'chunk': final_chunks[i]['chunk'],
                'knowledge_name': final_chunks[i]['knowledge_name']
            }
            metadata.append(data)
        
        upsert_data = list(zip(uuid, embeds, metadata))
        return upsert_data
    
    def install_pinecone_knowledge(self, index, upsert_data):
        try:
            pinecone.init(api_key=self.api_key, environment=self.environment)
            pinecone_index = pinecone.Index(index.name)
            pinecone_index.upsert(vectors=upsert_data)
            data = {"success": True}
        except:
            data = {"success": False}
        return data