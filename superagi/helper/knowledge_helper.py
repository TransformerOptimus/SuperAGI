from sqlalchemy.orm import Session
import boto3
import json
from superagi.config.config import get_config
from superagi.models.knowledge_config import KnowledgeConfig
from superagi.models.index_config import VectorIndexConfig

class KnowledgeHelper:
     
    def __init__(self, session = Session):
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
    
    def get_json_from_s3(self,file_path):
        s3 = boto3.client(
                's3',
                aws_access_key_id=get_config("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=get_config("AWS_SECRET_ACCESS_KEY"),
            )
        bucket_name = get_config("BUCKET_NAME")
        file = s3.Object(Bucket=bucket_name, Key=file_path)
        file = file.get()
        s3_response = file.get('Body')
        s3_content = s3_response.read().decode()
        json_data = json.loads(s3_content)
        return json_data