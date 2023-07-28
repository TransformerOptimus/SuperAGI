from sqlalchemy import Column, Integer, String, DateTime, Sequence
from superagi.models.base_model import DBBaseModel
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Models(DBBaseModel):
    """

    Represents a Model Record in the database

    Attributes:
        id (Integer): The unique identifier of the event.
        name (string): The unique name for the model.
        repo_link (string)
        repo_version_id (string)
        model_provider_id (int): The unique id of the model provider connecting to model_provider model.

    """

    __tablename__ = 'models'

    id = Column(Integer, primary_key = True)
    name = Column(String, nullable = False)
    repo_link = Column(String, nullable = False)
    repo_version_id = Column(String, nullable = False)
    model_provider_id = Column(Integer, nullable = False)

    def __repr__(self):
        """
        Returns a string representation of the Model Instance
        """

        return f"Event(id={self.id}, model_name={self.name}, "\
               f"repo_link={self.repo_link}, "\
               f"repo_version_id={self.repo_version_id}, "\
               f"model_provider_id={self.model_provider_id})"