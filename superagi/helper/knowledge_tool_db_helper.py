import pinecone
import openai
from qdrant_client import models, QdrantClient
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from superagi.config.config import get_config
from sqlalchemy.orm import Session



class PineconeCreds:
  def __init__(self,api_key, environment):
        self.api_key = api_key
        self.environment = environment
       
class QdrantCreds:
  def __init__(self,api_key, url, port):
        self.api_key = api_key
        self.url = url
        self.port = port

class KnowledgeToolDbHelper:
  def __init__(self,session):
     self.session = session
    
  
  def get_knowledge_details(self,knowledge):
    knowledge_name = knowledge.name
    knowledge_index_or_collection_id = knowledge.index_id
    knowledge_vector_db_index = self.session.query(VectorIndexCollection).filter(VectorIndexCollection.id == knowledge_index_or_collection_id).first()
    knowledge_vector_db = self.session.query(Vectordb).filter(Vectordb.id == knowledge_vector_db_index.vector_db_id).first()
    knowledge_vector_db_type = knowledge_vector_db.db_type
    knowledge_vector_db_id = knowledge_vector_db.id
    return {"knowledge_name" : knowledge_name,
            "knowledge_index_or_collection_id" : knowledge_index_or_collection_id,
            "knowledge_vector_db_index_name" : knowledge_vector_db_index.name,
            "knowledge_vector_db_type" : knowledge_vector_db_type,
            "knowledge_vector_db_id" : knowledge_vector_db_id}


  def get_pinecone_creds(self,knowledge_vector_db_id):
    pinecone_api_key = self.session.query(VectordbConfig).filter(VectordbConfig.id == knowledge_vector_db_id,VectordbConfig.key=="api_key").first()
    pinecone_environment = self.session.query(VectordbConfig).filter(VectordbConfig.id == knowledge_vector_db_id,VectordbConfig.key=="environment").first()
    pinecone_config = PineconeCreds(pinecone_api_key.value,pinecone_environment.value)
    return pinecone_config

  def get_qdrant_creds(self,knowledge_vector_db_id):
    qdrant_api_key = self.session.query(VectordbConfig).filter(VectordbConfig.id == knowledge_vector_db_id,VectordbConfig.key=="api_key").first()
    qdrant_url = self.session.query(VectordbConfig).filter(VectordbConfig.id == knowledge_vector_db_id,VectordbConfig.key=="url").first()
    qdrant_port = self.session.query(VectordbConfig).filter(VectordbConfig.id == knowledge_vector_db_id,VectordbConfig.key=="port").first()
    qdrant_config = QdrantCreds(qdrant_api_key.value,qdrant_url.value,qdrant_port.value)
    return qdrant_config
    


















  
  
