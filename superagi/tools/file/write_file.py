import os
from typing import Type
from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool
from superagi.config.config import get_config
from sqlalchemy.orm import sessionmaker
from superagi.models.db import connect_db
from superagi.helper.resource_helper import ResourceHelper
# from superagi.helper.s3_helper import upload_to_s3
from superagi.helper.s3_helper import S3Helper




class WriteFileInput(BaseModel):
    """Input for CopyFileTool."""
    file_name: str = Field(..., description="Name of the file to write. Only include the file name. Don't include path.")
    content: str = Field(..., description="File content to write")


class WriteFileTool(BaseTool):
    name: str = "Write File"
    args_schema: Type[BaseModel] = WriteFileInput
    description: str = "Writes text to a file"
    agent_id: int = None

    def _execute(self, file_name: str, content: str):
        engine = connect_db()
        Session = sessionmaker(bind=engine)
        session = Session()

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
            with open(final_path, 'rb') as file:
                resource = ResourceHelper.make_written_file_resource(file_name=file_name,
                                                      agent_id=self.agent_id,file=file,channel="OUTPUT")
                if resource is not None:
                    session.add(resource)
                    session.commit()
                    session.flush()
                    if resource.storage_type == "S3":
                        s3_helper = S3Helper()
                        s3_helper.upload_file(file, path=resource.path)
                        print("Resource Uploaded to S3!")
                session.close()
            return f"File written to successfully - {file_name}"
        except Exception as err:
            return f"Error: {err}"
