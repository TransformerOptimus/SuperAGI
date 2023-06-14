from sqlalchemy import Column, Integer, String, Boolean, DefaultClause
from superagi.models.base_model import DBBaseModel


# from pydantic import BaseModel

class Tool(DBBaseModel):
    __tablename__ = 'tools'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    description = Column(String)
    folder_name = Column(String)
    class_name = Column(String)
    file_name = Column(String)
    tool_kit_id = Column(Integer)
    is_deleted = Column(Boolean)

    def __repr__(self):
        return f"Tool(id={self.id}, name='{self.name}',description='{self.description}' folder_name='{self.folder_name}'," \
               f" file_name = {self.file_name}, class_name='{self.class_name}, tool_kit_id={self.tool_kit_id}')"
