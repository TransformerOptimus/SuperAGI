from sqlalchemy import Column, Integer, String
from superagi.models.base_model import DBBaseModel

class Models(DBBaseModel):
    """
    Represents a Model record in the database

    Attributes:
        id (Integer): The unique identifier of the event.
        model_name (String): The name of the model.
        description (String): The description for the model.
        end_point (String): The end_point for the model.
        model_provider_id (Integer): The unique id of the model_provider from the models_config table.
    """

    __tablename__ = 'models'

    id = Column(Integer, primary_key=True)
    model_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    end_point = Column(String, nullable=False)
    model_provider_id = Column(Integer, nullable=False)

    def __repr__(self):
        """
        Returns a string representation of the Models instance.
        """
        return f"Models(id={self.id}, model_name={self.model_name}, " \
               f"end_point={self.end_point}, model_provider_id={self.model_provider_id})"