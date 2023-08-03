from sqlalchemy import Column, Integer, String

from superagi.models.base_model import DBBaseModel


# from pydantic import BaseModel

class Tool(DBBaseModel):
    """
    Model representing a tool.

    Attributes:
        id (Integer): The primary key of the tool.
        name (String): The name of the tool.
        folder_name (String): The folder name of the tool.
        class_name (String): The class name of the tool.
        file_name (String): The file name of the tool.
    """

    __tablename__ = 'tools'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    description = Column(String)
    folder_name = Column(String)
    class_name = Column(String)
    file_name = Column(String)
    toolkit_id = Column(Integer)

    def __repr__(self):
        """
        Returns a string representation of the Tool object.

        Returns:
            str: String representation of the Tool object.
        """

        return f"Tool(id={self.id}, name='{self.name}',description='{self.description}' folder_name='{self.folder_name}'," \
               f" file_name = {self.file_name}, class_name='{self.class_name}, toolkit_id={self.toolkit_id}')"

    def to_dict(self):
        """
        Convert the Tool instance to a dictionary.

        Returns:
            dict: A dictionary representation of the Tool instance.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "folder_name": self.folder_name,
            "class_name": self.class_name,
            "file_name": self.file_name,
            "toolkit_id": self.toolkit_id
        }
    @staticmethod
    def add_or_update(session, tool_name: str, description: str, folder_name: str, class_name: str, file_name: str,
                      toolkit_id: int):
        # Check if a record with the given tool name already exists inside a toolkit
        tool = session.query(Tool).filter_by(name=tool_name,
                                             toolkit_id=toolkit_id).first()
        if tool is not None:
            # Update the attributes of the existing tool record
            tool.folder_name = folder_name
            tool.class_name = class_name
            tool.file_name = file_name
            tool.description = description
        else:
            # Create a new tool record
            tool = Tool(name=tool_name, description=description, folder_name=folder_name, class_name=class_name,
                        file_name=file_name,
                        toolkit_id=toolkit_id)
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
            session.flush()

    @classmethod
    def convert_tool_names_to_ids(cls, db, tool_names):
        """
        Converts a list of tool names to their corresponding IDs.

        Args:
            db: The database session.
            tool_names (list): List of tool names.

        Returns:
            list: List of tool IDs.
        """

        tools = db.session.query(Tool).filter(Tool.name.in_(tool_names)).all()
        return [tool.id for tool in tools]

    @classmethod
    def convert_tool_ids_to_names(cls, db, tool_ids):
        """
        Converts a list of tool IDs to their corresponding names.

        Args:
            db: The database session.
            tool_ids (list): List of tool IDs.

        Returns:
            list: List of tool names.
        """

        tools = db.session.query(Tool).filter(Tool.id.in_(tool_ids)).all()
        return [str(tool.name) for tool in tools]

    @classmethod
    def get_invalid_tools(cls, tool_ids, session):
        invalid_tool_ids = []
        for tool_id in tool_ids:
            tool = session.query(Tool).get(tool_id)
            if tool is None:
                invalid_tool_ids.append(tool_id)
        return invalid_tool_ids

    @classmethod
    def get_toolkit_tools(cls, session, toolkit_id : int):
        return session.query(Tool).filter(Tool.toolkit_id == toolkit_id).all()