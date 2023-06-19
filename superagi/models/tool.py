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
    folder_name = Column(String)
    class_name = Column(String)
    file_name = Column(String)

    def __repr__(self):
        """
        Returns a string representation of the Tool object.

        Returns:
            str: String representation of the Tool object.
        """

        return f"Tool(id={self.id}, name='{self.name}', folder_name='{self.folder_name}', class_name='{self.class_name}')"

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
