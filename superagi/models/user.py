from sqlalchemy import Column, Integer, String

from superagi.models.base_model import DBBaseModel


# from pydantic import BaseModel

class User(DBBaseModel):
    """
    Model representing a user.

    Attributes:
        id (Integer): The primary key of the user.
        name (String): The name of the user.
        email (String): The email of the user.
        password (String): The password of the user.
        organisation_id (Integer): The ID of the associated organisation.
    """

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    organisation_id = Column(Integer)

    def __repr__(self):
        """
        Returns a string representation of the User object.

        Returns:
            str: String representation of the User object.
        """

        return f"User(id={self.id}, name='{self.name}', email='{self.email}', password='{self.password}'," \
               f"organisation_id={self.organisation_id})"
