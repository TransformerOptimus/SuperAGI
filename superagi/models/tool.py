from sqlalchemy import Column, Integer, String

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

    def __repr__(self):
        return f"Tool(id={self.id}, name='{self.name}',description='{self.description}' folder_name='{self.folder_name}'," \
               f" file_name = {self.file_name}, class_name='{self.class_name}, tool_kit_id={self.tool_kit_id}')"

    @staticmethod
    def add_or_update(session, tool_name: str, description: str, folder_name: str, class_name: str, file_name: str,
                      tool_kit_id: int):
        # Check if a record with the given tool name already exists inside a toolkit
        tool = session.query(Tool).filter_by(name=tool_name,
                                             tool_kit_id=tool_kit_id).first()
        print("____ADD OR UPDATE TOOL KIT")
        if tool is not None:
            # Update the attributes of the existing tool record
            print("UPDATED TOOL KIT")
            tool.folder_name = folder_name
            tool.class_name = class_name
            tool.file_name = file_name
            tool.description = description
        else:
            # Create a new tool record
            print("CREATED TOOL KIT")
            tool = Tool(name=tool_name, description=description, folder_name=folder_name, class_name=class_name,
                        file_name=file_name,
                        tool_kit_id=tool_kit_id)
            session.add(tool)

        session.commit()
        session.flush()
        return tool

    @staticmethod
    def delete_tool(session, tool_name):
        tool = session.query(Tool).filter(Tool.name == tool_name).first()
        if tool:
            session.delete(tool)
            session.commit()
