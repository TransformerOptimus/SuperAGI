import boto3
from superagi.config.config import get_config
from fastapi import HTTPException
from superagi.lib.logger import logger

class S3Helper:
    def __init__(self):
        """
        Initialize the S3Helper class.
        Using the AWS credentials from the configuration file, create a boto3 client.
        """
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=get_config("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=get_config("AWS_SECRET_ACCESS_KEY"),
        )
        self.bucket_name = get_config("BUCKET_NAME")

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
