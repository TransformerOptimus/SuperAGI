import os
from typing import Type
from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool
from superagi.config.config import get_config
from superagi.models.resource import Resource
from sqlalchemy.orm import sessionmaker
from superagi.models.db import connect_db
import datetime
import boto3
from botocore.exceptions import NoCredentialsError
from fastapi import HTTPException, Depends, Request





def upload_to_s3(file,path):
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=get_config("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=get_config("AWS_SECRET_ACCESS_KEY"),
        )
        bucket_name = get_config("BUCKET_NAME")
        s3.upload_fileobj(file, bucket_name, path)
        print("File uploaded in S3 successfully!")
    except:
        raise HTTPException(status_code=500, detail="AWS credentials not found. Check your configuration.")

def make_written_file_resource(file_name: str, agent_id: int,file):
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
        resource = Resource(name=file_name, path=path + "/" + file_name, storage_type=storage_type, size=file_size,
                            type=file_type,
                            channel="OUTPUT",
                            agent_id=agent_id)
        return resource
    elif storage_type == "S3":
        file_name = file_name.split('.')
        path = 'input/' + file_name[0] + '_' + str(datetime.datetime.now()).replace(' ', '').replace('.', '').replace(
            ':', '') + '.' + file_name[1]
        try:
            resource = Resource(name=file_name, path=path + "/" + file_name, storage_type=storage_type, size=file_size,
                                type=file_type,
                                channel="OUTPUT",
                                agent_id=agent_id)
            return resource
        except NoCredentialsError:
            raise HTTPException(status_code=500, detail="AWS credentials not found. Check your configuration.")



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
                resource = make_written_file_resource(file_name=file_name,
                                                      agent_id=self.agent_id,file=file)
                print("Resource",resource)
                if resource is not None:
                    session.add(resource)
                    session.commit()
                    session.flush()
                    if resource.storage_type == "S3":
                        upload_to_s3(file, path=resource.path)
                session.close()
            return f"File written to successfully - {file_name}"
        except Exception as err:
            return f"Error: {err}"
