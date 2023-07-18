from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker

from superagi.helper.encyption_helper import decrypt_data
from superagi.models.base_model import DBBaseModel
from superagi.models.db import connect_db

engine = connect_db()
Session = sessionmaker(bind=engine)


class Configuration(DBBaseModel):
    """
    General org level configurations are stored here

    Attributes:
        id (Integer): The primary key of the configuration.
        organisation_id (Integer): The ID of the organization associated with the configuration.
        key (String): The configuration key.
        value (Text): The configuration value.
    """

    __tablename__ = 'configurations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    organisation_id = Column(Integer)
    key = Column(String)
    value = Column(Text)

    def __repr__(self):
        """
        Returns a string representation of the Configuration object.

        Returns:
            str: String representation of the Configuration object.
        """

        return f"Config(id={self.id}, organisation_id={self.organisation_id}, key={self.key}, value={self.value})"

    @classmethod
    def get_model_api_key(cls, organisation_id):
        """
        Returns the model api key for the given organisation id.

        Args:
            organisation_id (int): The identifier of the organisation.

        Returns:
            str: The model api key.
        """
        session = Session()
        model_api_key = session.query(cls).filter(cls.organisation_id == organisation_id,
                                                  cls.key == 'model_api_key').first()
        session.close()
        return decrypt_data(model_api_key.value) if model_api_key else None
