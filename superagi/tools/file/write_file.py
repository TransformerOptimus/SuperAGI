import os
from typing import Type
from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool
from superagi.config.config import get_config
from superagi.models.resource import Resource
from sqlalchemy.orm import sessionmaker
from superagi.models.db import connectDB

engine = connectDB()
Session = sessionmaker(bind=engine)
session = Session()

def make_written_file_resource(file_name: str,agent_id:int):
    path = get_config("RESOURCES_OUTPUT_ROOT_DIR")
    storage_type = get_config("STORAGE_TYPE")
    file_type = "application/txt"

    root_dir = get_config('RESOURCES_OUTPUT_ROOT_DIR')

    if root_dir is not None:
        root_dir = root_dir if root_dir.startswith("/") else os.getcwd() + "/" + root_dir
        root_dir = root_dir if root_dir.endswith("/") else root_dir + "/"
        final_path = root_dir + file_name
    else:
        final_path = os.getcwd() + "/" + file_name
    file_size = os.path.getsize(final_path)
    resource = None
    if storage_type == "FILE":
        # Save Resource to Database
        resource = Resource(name=file_name, path=path + "/" + file_name, storage_type=storage_type, size=file_size,
                            type=file_type,
                            channel="OUTPUT",
                            agent_id=agent_id)
    elif storage_type == "S3":
        pass
    return resource

class WriteFileInput(BaseModel):
    """Input for CopyFileTool."""
    file_name: str = Field(..., description="Name of the file to write")
    content: str = Field(..., description="File content to write")
    agent_id: int = Field(..., description="Agent ID associated with the File")


class WriteFileTool(BaseTool):
    name: str = "Write File"
    args_schema: Type[BaseModel] = WriteFileInput
    description: str = "Writes text to a file"
    agent_id: int = None

    def _execute(self, file_name: str, content: str, agent_id: int):
        final_path = file_name
        root_dir = get_config('RESOURCES_OUTPUT_ROOT_DIR')
        if root_dir is not None:
            root_dir = root_dir if root_dir.startswith("/") else os.getcwd() + "/" + root_dir
            root_dir = root_dir if root_dir.endswith("/") else root_dir + "/"
            final_path = root_dir + file_name
        else:
            final_path = os.getcwd() + "/" + file_name

        try:
            with open(final_path, 'w', encoding="utf-8") as file:
                file.write(content)
                file.close()
                resource = make_written_file_resource(file_name=file_name,
                                                      agent_id=agent_id)
                if resource is not None:
                    session.add(resource)
                    session.commit()
            return f"File written to successfully - {file_name}"
        except Exception as err:
            return f"Error: {err}"