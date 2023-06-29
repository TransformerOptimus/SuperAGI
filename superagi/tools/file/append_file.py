import os
from typing import Type

from pydantic import BaseModel, Field

from superagi.helper.resource_helper import ResourceHelper
from superagi.tools.base_tool import BaseTool


class AppendFileInput(BaseModel):
    """Input for CopyFileTool."""
    file_name: str = Field(..., description="Name of the file to write")
    content: str = Field(..., description="The text to append to the file")


class AppendFileTool(BaseTool):
    """
    Append File tool

    Attributes:
        name : The name.
        agent_id: The agent id.
        description : The description.
        args_schema : The args schema.
    """
    name: str = "Append File"
    agent_id: int = None
    args_schema: Type[BaseModel] = AppendFileInput
    description: str = "Append text to a file"

    def _execute(self, file_name: str, content: str):
        """
        Execute the append file tool.

        Args:
            file_name : The name of the file to write.
            content : The text to append to the file.

        Returns:
            success or error message.
        """
        final_path = ResourceHelper.get_root_output_dir() + file_name
        if "{agent_id}" in final_path:
            final_path = final_path.replace("{agent_id}", str(self.agent_id))
        try:
            directory = os.path.dirname(final_path)
            os.makedirs(directory, exist_ok=True)
            with open(final_path, 'a', encoding="utf-8") as file:
                file.write(content)
            return "File written to successfully."
        except Exception as err:
            return f"Error: {err}"
