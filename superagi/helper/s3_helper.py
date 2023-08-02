import boto3
from superagi.config.config import get_config
from fastapi import HTTPException
from superagi.lib.logger import logger
import json


class S3Helper:
    def __init__(self):
        """
        Initialize the S3Helper class.
        Using the AWS credentials from the configuration file, create a boto3 client.
        """
        self.s3 = S3Helper.__get_s3_client()
        self.bucket_name = get_config("BUCKET_NAME")

    @classmethod
    def __get_s3_client(cls):
        """
        Get an S3 client.

        Returns:
            s3 (S3Helper): The S3Helper object.
        """
        return boto3.client(
            's3',
            aws_access_key_id=get_config("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=get_config("AWS_SECRET_ACCESS_KEY"),
        )

    def upload_file(self, file, path):
        """
        Upload a file to S3.

        Args:
            file (FileStorage): The file to upload.
            path (str): The path to upload the file to.

        Raises:
            HTTPException: If the AWS credentials are not found.

        Returns:
            None
        """
        try:
            self.s3.upload_fileobj(file, self.bucket_name, path)
            logger.info("File uploaded to S3 successfully!")
        except:
            raise HTTPException(status_code=500, detail="AWS credentials not found. Check your configuration.")

    def check_file_exists_in_s3(self, file_path):
        response = self.s3.list_objects_v2(Bucket=get_config("BUCKET_NAME"), Prefix="resources" + file_path)
        return 'Contents' in response

    def read_from_s3(self, file_path):
        file_path = "resources" + file_path
        logger.info(f"Reading file from s3: {file_path}")
        response = self.s3.get_object(Bucket=get_config("BUCKET_NAME"), Key=file_path)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return response['Body'].read().decode('utf-8')
        raise Exception(f"Error read_from_s3: {response}")
    
    def read_binary_from_s3(self, file_path):
        file_path = "resources" + file_path
        logger.info(f"Reading file from s3: {file_path}")
        response = self.s3.get_object(Bucket=get_config("BUCKET_NAME"), Key=file_path)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return response['Body'].read()
        raise Exception(f"Error read_from_s3: {response}")
    
    def get_json_file(self, path):
        """
        Get a JSON file from S3.
        Args:
            path (str): The path to the JSON file.
        Raises:
            HTTPException: If the AWS credentials are not found.
        Returns:
            dict: The JSON file.
        """
        try:
            obj = self.s3.get_object(Bucket=self.bucket_name, Key=path)
            s3_response =  obj['Body'].read().decode('utf-8')
            return json.loads(s3_response)
        except:
            raise HTTPException(status_code=500, detail="AWS credentials not found. Check your configuration.")

    def delete_file(self, path):
        """
        Delete a file from S3.

        Args:
            path (str): The path to the file to delete.

        Raises:
            HTTPException: If the AWS credentials are not found.

        Returns:
            None
        """
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=path)
            logger.info("File deleted from S3 successfully!")
        except:
            raise HTTPException(status_code=500, detail="AWS credentials not found. Check your configuration.")