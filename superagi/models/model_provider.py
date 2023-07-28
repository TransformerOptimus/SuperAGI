from sqlalchemy import Column, Integer, String, Sequence, DateTime
from superagi.models.base_model import DBBaseModel
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ModelProvider(DBBaseModel):
    """
    Represents a ModelProvider record in the database.

    Attributes:
        id (Integer): The unique identifier of the model provider.
        name (String): The name of the model provider.
        api_key (String): The API key for the model provider.
        endpoint (String): The endpoint for the model provider.
    """

    __tablename__ = 'model_provider'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    api_key = Column(String, nullable=False)
    endpoint = Column(String, nullable=False)

    def __repr__(self):
        """
        Returns a string representation of the ModelProvider instance.
        """

        return f"ModelProvider(id={self.id}, name={self.name}, api_key={self.api_key}, endpoint={self.endpoint})"