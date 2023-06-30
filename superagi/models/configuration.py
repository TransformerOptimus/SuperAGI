from sqlalchemy import Column, Integer, String,Text
from superagi.models.base_model import DBBaseModel


class Configuration(DBBaseModel):
    """
    Model representing a configuration.

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
