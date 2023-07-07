from sqlalchemy import Column, Integer, String,Text

from superagi.helper.encyption_helper import decrypt_data
from superagi.models.base_model import DBBaseModel


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
    def fetch_configuration(cls, session, organisation_id: int, key: str, default_value=None) -> str:
        """
        Fetches the configuration of an agent.

        Args:
            session: The database session object.
            organisation_id (int): The ID of the organisation.
            key (str): The key of the configuration.
            default_value (str): The default value of the configuration.

        Returns:
            dict: Parsed configuration.

        """

        configuration = session.query(Configuration).filter_by(organisation_id=organisation_id, key=key).first()
        return decrypt_data(configuration.value) if configuration else default_value