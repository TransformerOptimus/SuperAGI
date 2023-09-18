from superagi.models.base_model import DBBaseModel
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, and_


class ReadmeContent(DBBaseModel):
    """
    Represents a Readme Content record in the database

    Attributes:
        id (Integer): The unique identifier of the event.
        content (String): The HTML content to be displayed.
        model_id (Integer): The unique identifier of the model from the Models table.
        org_id (Integer): The ID of the organisation.
    """

    __tablename__ = 'models_readme_content'

    id = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)
    model_id = Column(Integer, nullable=False)
    org_id = Column(Integer, nullable=False)

    def __repr__(self):
        """
        Represents a string representation of the Readme Content instance.
        """

        return f"ModelsReadmeContent(id={self.id}, content={self.content}, " \
               f"model_id={self.model_id}, org_id={self.org_id})"

