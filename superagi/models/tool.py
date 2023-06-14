from sqlalchemy import Column, Integer, String
from superagi.models.base_model import DBBaseModel


# from pydantic import BaseModel

class Tool(DBBaseModel):
    __tablename__ = 'tools'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    folder_name = Column(String)
    class_name = Column(String)
    file_name = Column(String)

    def __repr__(self):
        return f"Tool(id={self.id}, name='{self.name}', folder_name='{self.folder_name}', class_name='{self.class_name}')"

    @classmethod
    def convert_tool_names_to_ids(cls, db, tool_names):
        tools = db.session.query(Tool).filter(Tool.name.in_(tool_names)).all()
        return [tool.id for tool in tools]

    @classmethod
    def convert_tool_ids_to_names(cls, db, tool_ids):
        tools = db.session.query(Tool).filter(Tool.id.in_(tool_ids)).all()
        return [str(tool.name) for tool in tools]
