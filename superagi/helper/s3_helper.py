import boto3
from superagi.config.config import get_config
from fastapi import HTTPException

class S3Helper:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=get_config("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=get_config("AWS_SECRET_ACCESS_KEY"),
        )
        self.bucket_name = get_config("BUCKET_NAME")

    def upload_file(self, file, path):
        try:
            self.s3.upload_fileobj(file, self.bucket_name, path)
            print("File uploaded to S3 successfully!")
        except:
            raise HTTPException(status_code=500, detail="AWS credentials not found. Check your configuration.")
