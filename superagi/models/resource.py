from sqlalchemy import Column, Integer, String, Float, Text
from superagi.models.base_model import DBBaseModel
from sqlalchemy.orm import sessionmaker


class Resource(DBBaseModel):
    """
    Model representing a resource.

    Attributes:
        id (Integer): The primary key of the resource.
        name (String): The name of the resource.
        storage_type (String): The storage type of the resource (FILESERVER, S3).
        path (String): The path of the resource (required for S3 storage type).
        size (Integer): The size of the resource.
        type (String): The type of the resource (e.g., application/pdf).
        channel (String): The channel of the resource (INPUT, OUTPUT).
        agent_id (Integer): The ID of the agent associated with the resource.
        agent_execution_id (Integer) : The ID of the agent execution corresponding to resource
    """

    __tablename__ = 'resources'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    storage_type = Column(String)  # FILESERVER,S3
    path = Column(String)  # need for S3
    size = Column(Integer)
    type = Column(String)  # application/pdf etc
    channel = Column(String)  # INPUT,OUTPUT
    agent_id = Column(Integer)
    agent_execution_id = Column(Integer)
    summary = Column(Text)

    def __repr__(self):
        """
        Returns a string representation of the Resource object.

        Returns:
            str: String representation of the Resource object.
        """

        return f"Resource(id={self.id}, name='{self.name}', storage_type='{self.storage_type}', path='{self.path}, size='{self.size}', type='{self.type}', channel={self.channel}, agent_id={self.agent_id}, agent_execution_id={self.agent_execution_id})"

    @staticmethod
    def validate_resource_type(storage_type):
        """
        Validates the resource type.

        Args:
            storage_type (str): The storage type to validate.

        Raises:
            InvalidResourceType: If the storage type is invalid.
        """

        valid_types = ["FILE", "S3"]

        if storage_type not in valid_types:
            raise InvalidResourceType("Invalid resource type")
    
    @classmethod
    def find_by_run_ids(cls, session, run_ids: list):
        db_resources_arr=session.query(Resource).filter(Resource.agent_execution_id.in_(run_ids)).all()
        return db_resources_arr
    
class InvalidResourceType(Exception):
    """Custom exception for invalid resource type"""
