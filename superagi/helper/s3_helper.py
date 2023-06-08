import boto3
from superagi.config.config import get_config
from fastapi import HTTPException, Depends, Request

s3 = boto3.client(
    's3',
    aws_access_key_id=get_config("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=get_config("AWS_SECRET_ACCESS_KEY"),
    )

def upload_to_s3(file,path):
    try:
        print("S3 helper")
        bucket_name = get_config("BUCKET_NAME")
        s3.upload_fileobj(file, bucket_name, path)
        print("File uploaded in S3 successfully!")
    except:
        raise HTTPException(status_code=500, detail="AWS credentials not found. Check your configuration.")
