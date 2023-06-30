from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import Session

from superagi.models.base_model import DBBaseModel
import json
import yaml



class OauthTokens(DBBaseModel):
    """
    Model representing a OauthTokens.

    Attributes:
        id (Integer): The primary key of the oauth token.
        user_id (Integer): The ID of the user associated with the Tokens.
        toolkit_id (Integer): The ID of the toolkit associated with the Tokens.
        key (String): The Token Key.
        value (Text): The Token value.
    """

    __tablename__ = 'oauth_tokens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    organisation_id = Column(Integer)
    toolkit_id = Column(Integer)
    key = Column(String)
    value = Column(Text)

    def __repr__(self):
        """
        Returns a string representation of the OauthTokens object.

        Returns:
            str: String representation of the OauthTokens object.
        """

        return f"Tokens(id={self.id}, user_id={self.user_id}, organisation_id={self.organisation_id} toolkit_id={self.toolkit_id}, key={self.key}, value={self.value})"
    
    @classmethod
    def add_or_update(self, session: Session, toolkit_id: int, user_id: int, organisation_id: int, key: str, value: Text = None):
        oauth_tokens = session.query(OauthTokens).filter_by(toolkit_id=toolkit_id, user_id=user_id).first()
        if oauth_tokens:
            # Update existing oauth tokens
            if value is not None:
                oauth_tokens.value = value
        else:
            # Create new oauth tokens
            oauth_tokens = OauthTokens(toolkit_id=toolkit_id, user_id=user_id, organisation_id=organisation_id, key=key, value=value)
            session.add(oauth_tokens)

        session.commit()