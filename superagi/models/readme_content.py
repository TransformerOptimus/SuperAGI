from superagi.models.base_model import DBBaseModel
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, and_
import logging

class ReadmeContent(DBBaseModel):
    """
    Represents a Readme Content record in the database

    Attributes:
        id (Integer): The unique identifier of the event.
        content (String): The HTML content to be displayed.
        model_id (Integer): The unique identifier of the model from the Models table.
        code_language (String): The language used of the code snippets.
        org_id (Integer): The ID of the organisation.
    """

    __tablename__ = 'models_readme_content'

    id = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)
    model_id = Column(Integer, nullable=False)
    code_language = Column(String, nullable=False)
    org_id = Column(Integer, nullable=False)

    def __repr__(self):
        """
        Represents a string representation of the Readme Content instance.
        """

        return f"ModelsReadmeContent(id={self.id}, content={self.content}, " \
               f"model_id={self.model_id}, code_language={self.code_language}, org_id={self.org_id})"

    @classmethod
    def fetch_model_readme(cls, session, organisation_id, model_id):
        try:
            readmes = session.query(ReadmeContent).filter(ReadmeContent.model_id == model_id,
                                                          ReadmeContent.org_id == organisation_id).all()
            if readmes:
                return [{'model_id': readme.model_id,
                         'org_id': readme.org_id,
                         'content': readme.content,
                         'language': readme.code_language,
                         } for readme in readmes]
            else:
                return {"error": "Readme not found"}
        except Exception as e:
            logging.error(f"Unexpected Error Occured: {e}")
            return {"error": "Unexpected Error Occured"}