from sqlalchemy.orm import Session
from superagi.models.vector_db_config import VectordbConfig
from qdrant_client import models, QdrantClient

class QdrantHelper:
    
    def __init__(self, session, api_key, url, port):
        self.session = session
        self.api_key = api_key
        self.url = url
        self.port = port
    
    def get_dimensions(self, index_name):
        try:
            qdrant_client = QdrantClient(
                api_key=self.api_key,
                url=self.url
            )
            collection_info = qdrant_client.get_collection(collection_name=index_name)
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
    
    def get_qdrant_index_state(self, index_name):
        try:
            qdrant_client = QdrantClient(
                api_key=self.api_key,
                url=self.url
            )
            collection_info = qdrant_client.get_collection(collection_name=index_name)
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
    
    def get_upsert_data(self, chunk_json):
        final_chunks = []
        for key in chunk_json.keys():
            final_chunks.append(chunk_json[key])
        
        uuid = []
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
        
        return {
            "ids": uuid,
            "payload": metadata,
            "vectors": embeds
        }
    
    def install_qdrant_knowledge(self, index, upsert_data):
        try:
            qdrant_client = QdrantClient(
                api_key=self.api_key,
                url=self.url
            )
        
            qdrant_client.upsert(
                collection_name=index.name,
                points=models.Batch(
                    ids=upsert_data["ids"],
                    payloads=upsert_data["payloads"],
                    vectors=upsert_data["vectors"]
                ),
            )
            data = {"success": True}
        except:
            data = {"success": False}
        return data
    
    def uninstall_qdrant_knowledge(self, index, vector_ids):
        try:
            qdrant_client = QdrantClient(
                api_key = self.api_key,
                url = self.url
            )

            qdrant_client.delete(
                collection_name = index.name,
                points_selector = models.PointIdsList(
                    points = vector_ids
                ),
            )
            
            data = {"success": True}
        except:
            data = {"success": False}

        return data