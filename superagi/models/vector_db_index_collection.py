from __future__ import annotations

from sqlalchemy import Column, Integer, String

# from superagi.models import AgentConfiguration
from superagi.models.base_model import DBBaseModel


class VectorIndexCollection(DBBaseModel):
    """
    Represents an vector db index.

    Attributes:
        id (int): The unique identifier of the index/collection also referred to as class in Weaviate.
        name (str): The name of the index/collection.
        vector_db_id (int): The identifier of the associated vector db.
    """

    __tablename__ = 'vector_db_index_collection'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    vector_db_id = Column(Integer)

    def __repr__(self):
        """
        Returns a string representation of the Vector db index object.

        Returns:
            str: String representation of the Vector db index.

        """
        return f"VectorDBIndexCollection(id={self.id}, name='{self.name}', vector_db_id={self.vector_db_id})" #, " \
               #f"description='{self.description}', agent_workflow_id={self.agent_workflow_id})"

    @classmethod
    def add_vector_index(session, index_name, vector_db_id):
        vector_index = VectorIndexCollection(name=index_name, vector_db_id=vector_db_id)
        session.add(vector_index)
        session.commit()
        return vector_index
    
    @classmethod
    def get_vector_index_organisation(session, vector_db_id):
        vector_indices = session.query(VectorIndexCollection).filter(VectorIndexCollection.vector_db_id == vector_db_id).all()
        return vector_indices
    
    @classmethod
    def delete_vector_index(session, id):
        session.query(VectorIndexCollection).filter(VectorIndexCollection.id == id).delete()
        session.commit()

    @classmethod
    def get_vector_index_from_id(session, id):
        index = session.query(VectorIndexCollection).filter(VectorIndexCollection.id == id).first()
        return index
        