from sqlalchemy.orm import Session
from superagi.models.knowledge_config import KnowledgeConfig
from superagi.models.index_config import VectorIndexConfig

class KnowledgeHelper:
     
    def __init__(self, session):
        self.session = session
    
    def check_valid_dimension(self, session, index_id, knowledge_id):
        knowledge_config = session.query(KnowledgeConfig).filter(KnowledgeConfig.knowledge_id == knowledge_id, KnowledgeConfig.key == "dimensions").first()
        knowledge_dimensions = knowledge_config.value
        index_config = session.query(VectorIndexConfig).filter(VectorIndexConfig.vector_index_id == index_id, VectorIndexConfig.key == "dimensions").first()
        index_dimensions = index_config.value
        if knowledge_dimensions == index_dimensions:
            return True
        else:
            return False