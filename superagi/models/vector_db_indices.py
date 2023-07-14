from __future__ import annotations

from sqlalchemy import Column, Integer, String

# from superagi.models import AgentConfiguration
from superagi.models.base_model import DBBaseModel


class VectordbIndices(DBBaseModel):
    """
    Represents an vector db index.
    Attributes:
        id (int): The unique identifier of the index/collection also referred to as class in Weaviate.
        name (str): The name of the index/collection.
        vector_db_id (int): The identifier of the associated vector db.
    """

    __tablename__ = 'vector_db_indices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    vector_db_id = Column(Integer)
    dimensions = Column(Integer)
    state = Column(String)

    def __repr__(self):
        """
        Returns a string representation of the Vector db index object.
        Returns:
            str: String representation of the Vector db index.
        """
        return f"VectordbIndices(id={self.id}, name='{self.name}', vector_db_id={self.vector_db_id}, dimensions={self.dimensions}, state={self.state})"
    
    @classmethod
    def get_vector_index_from_id(cls, session, vector_db_index_id):
        vector_db_index = session.query(VectordbIndices).filter(VectordbIndices.id == vector_db_index_id).first()
        return vector_db_index