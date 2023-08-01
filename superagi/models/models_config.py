from sqlalchemy import Column, Integer, String
from superagi.models.base_model import DBBaseModel

class ModelsConfig(DBBaseModel):
    """
    Represents a Model Config record in the database.

    Attributes:
        id (Integer): The unique identifier of the event.
        source_name (String): The name of the model provider.
        api_key (String): The api_key for individual model providers for every Organisation
        org_id (Integer): The ID of the organisation.
    """

    __tablename__ = 'models_config'

    id = Column(Integer, primary_key=True)
    source_name = Column(String, nullable=False)
    api_key = Column(String, nullable=False)
    org_id = Column(Integer, nullable=False)

    def __repr__(self):
        """
        Returns a string representation of the ModelsConfig instance.
        """
        return f"ModelsConfig(id={self.id}, source_name={self.source_name}, " \
               f"org_id={self.org_id})"