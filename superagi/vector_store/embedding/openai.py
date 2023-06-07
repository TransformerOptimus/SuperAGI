import os
from abc import ABC, abstractmethod
from superagi.config.config import get_config
import openai
from sqlalchemy.orm import sessionmaker

from superagi.models.configuration import Configuration
from superagi.models.db import connect_db

class BaseEmbedding(ABC):

  @abstractmethod
  def get_embedding(self, text):
    pass

class OpenAiEmbedding:
    def __init__(self, model_api_key, model="text-embedding-ada-002"):
        self.model = model
        self.model_api_key = model_api_key

    async def get_embedding_async(self, text):
        try:
            # openai.api_key = get_config("OPENAI_API_KEY")
            openai.api_key = self.model_api_key
            response = await openai.Embedding.create(
                input=[text],
                engine=self.model
            )
            return response['data'][0]['embedding']
        except Exception as exception:
            return {"error": exception}

    def get_embedding(self, text):
        try:
            # openai.api_key = get_config("OPENAI_API_KEY")
            # openai.api_key =
            engine = connect_db()
            Session = sessionmaker(bind=engine)
            session = Session()
            configuration = session.query(Configuration).filter_by(organisation_id=organisation_id, key=key).first()

            response = openai.Embedding.create(
                input=[text],
                engine=self.model
            )
            return response['data'][0]['embedding']
        except Exception as exception:
            return {"error": exception}
