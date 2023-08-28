from sqlalchemy import JSON, Boolean, Column, Integer, String

from superagi.models.base_model import DBBaseModel


class Webhooks(DBBaseModel):
    """

    Attributes:


    Methods:
    """

    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    org_id = Column(Integer)
    url = Column(String)
    headers = Column(JSON)
    is_deleted = Column(Boolean)
