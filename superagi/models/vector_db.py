from __future__ import annotations
import requests

from sqlalchemy import Column, Integer, String

# from superagi.models import AgentConfiguration
from superagi.models.base_model import DBBaseModel

#marketplace_url = "https://app.superagi.com/api"
marketplace_url = "http://localhost:3000/api"

class Vectordb(DBBaseModel):
    """
    Represents an vector db entity.

    Attributes:
        id (int): The unique identifier of the agent.
        name (str): The name of the database.
        db_type (str): The name of the db agent.
        organisation_id (int): The identifier of the associated organisation.
    """

    __tablename__ = 'vector_db'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    db_type = Column(String)
    organisation_id = Column(Integer)

    def __repr__(self):
        """
        Returns a string representation of the Vector db object.

        Returns:
            str: String representation of the Vector db.

        """
        return f"Vector(id={self.id}, name='{self.name}', db_type='{self.db_type}' organisation_id={self.organisation_id}"


    @classmethod
    def fetch_marketplace_list(cls, session, organisation_id):
        vector_dbs = session.query(Vectordb).filter(Vectordb.organisation_id == organisation_id).all()
        return vector_dbs
    
    @classmethod
    def add_database(session, name, db_type, organisation):
        vector_db = Vectordb(name=name, db_type=db_type, organisation_id=organisation.id)
        session.add(vector_db)
        session.commit()
        return vector_db
    
    @classmethod
    def get_vector_db_organisation(session, organisation):
        vector_db = session.query(Vectordb).filter(Vectordb.organisation_id == organisation.id).all()
        vector_db_list = []
        for vector in vector_db:
            vector_data = {
                "id": vector.id,
                "name": vector.name,
                "db_type": vector.db_type
            }
            vector_db_list.append(vector_data)
        return vector_db_list
    
    @classmethod
    def delete_vector_db(session, vector_db_id):
        session.query(Vectordb).filter(Vectordb.id == vector_db_id).delete()
        session.commit()
