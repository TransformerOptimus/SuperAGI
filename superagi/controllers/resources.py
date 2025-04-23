import datetime
import os
import re
import secrets
from pathlib import Path

import boto3
from botocore.exceptions import NoCredentialsError
from fastapi import APIRouter
from fastapi import File, Form, UploadFile
from fastapi import HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_sqlalchemy import db

from superagi.config.config import get_config
from superagi.helper.auth import check_auth
from superagi.helper.resource_helper import ResourceHelper
from superagi.lib.logger import logger
from superagi.models.agent import Agent
from superagi.models.resource import Resource
from superagi.worker import summarize_resource
from superagi.types.storage_types import StorageType

router = APIRouter()

s3 = boto3.client(
    's3',
    aws_access_key_id=get_config("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=get_config("AWS_SECRET_ACCESS_KEY"),
)


def sanitize_filename(filename):
    """
    Sanitize a filename by removing any path components and suspicious patterns.
    
    Args:
        filename (str): The filename to sanitize.
        
    Returns:
        str: The sanitized filename.
    """
    # Remove any path components, keep only the basename
    sanitized = os.path.basename(filename)
    sanitized = sanitized.replace('\0', '')
    
    suspicious_patterns = ['..', '~', '/', '\\', '%00', '%0A']
    for pattern in suspicious_patterns:
        if pattern in filename:
            logger.warning(f"Suspicious pattern '{pattern}' detected in filename: {filename}")
            raise HTTPException(status_code=400, detail="Invalid characters in filename")
    
    # Ensure the filename only contains allowed characters
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9._-]*$', sanitized):
        raise HTTPException(status_code=400, detail="Filename contains invalid characters")
    
    return sanitized


def validate_file_path(file_path, base_directory):
    """
    Validate that a file path is within the allowed base directory.
    
    Args:
        file_path (str): The file path to validate.
        base_directory (str): The base directory that the file path must be within.
        
    Returns:
        bool: True if the file path is valid, False otherwise.
    """
    # Normalize paths for comparison
    abs_file_path = os.path.abspath(file_path)
    abs_base_dir = os.path.abspath(base_directory)
    
    # Check if the file path is within the base directory
    if not abs_file_path.startswith(abs_base_dir):
        logger.warning(f"Path traversal attempt detected: {file_path} is outside {base_directory}")
        return False
        
    # Additional checks for suspicious patterns
    if '..' in file_path or '~' in file_path or '%' in file_path:
        logger.warning(f"Suspicious patterns detected in path: {file_path}")
        return False
        
    return True


@router.post("/add/{agent_id}", status_code=201)
async def upload(agent_id: int, file: UploadFile = File(...), name=Form(...), size=Form(...), type=Form(...),
                 Authorize: AuthJWT = Depends(check_auth)):
    """
    Upload a file as a resource for an agent.

    Args:
        agent_id (int): ID of the agent.
        file (UploadFile): Uploaded file.
        name (str): Name of the resource.
        size (str): Size of the resource.
        type (str): Type of the resource.

    Returns:
        Resource: Uploaded resource.

    Raises:
        HTTPException (status_code=400): If the agent with the specified ID does not exist.
        HTTPException (status_code=400): If the file type is not supported.
        HTTPException (status_code=500): If AWS credentials are not found or if there is an issue uploading to S3.

    """

    agent = db.session.query(Agent).filter(Agent.id == agent_id).first()
    if agent is None:
        raise HTTPException(status_code=400, detail="Agent does not exist")

    # Check for path traversal attempts in both filename and name parameters
    if '..' in file.filename or '..' in name or '/' in name or '\\' in name:
        logger.warning(f"Path traversal attempt detected: filename={file.filename}, name={name}")
        raise HTTPException(status_code=400, detail="Invalid filename or name - path traversal detected")

    # Sanitize the filename (this will throw an exception if the filename is suspicious)
    try:
        original_filename = sanitize_filename(file.filename)
    except HTTPException as e:
        logger.warning(f"Filename sanitization failed: {file.filename}")
        raise e

    # Validate name parameter separately as it might be different from filename
    try:
        sanitized_name = sanitize_filename(name)
    except HTTPException as e:
        logger.warning(f"Name sanitization failed: {name}")
        raise e

    # Extract and validate file extension
    accepted_file_types = (".pdf", ".docx", ".pptx", ".csv", ".txt", ".epub")
    _, ext = os.path.splitext(original_filename)
    if ext.lower() not in accepted_file_types:
        raise HTTPException(status_code=400, detail=f"File type {ext} not supported! Allowed types: {', '.join(accepted_file_types)}")
        
    # Determine storage directory
    storage_type = StorageType.get_storage_type(get_config("STORAGE_TYPE", StorageType.FILE.value))
    save_directory = ResourceHelper.get_root_input_dir()
    if "{agent_id}" in save_directory:
        save_directory = ResourceHelper.get_formatted_agent_level_path(agent=Agent
                                                                       .get_agent_from_id(session=db.session,
                                                                                    agent_id=agent_id),
                                                                       path=save_directory)
    
    # Create a secure filename with random token to prevent guessing
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    random_token = secrets.token_hex(8)  # 16 character random hex string
    secure_filename = f"{timestamp}_{random_token}_{original_filename}"
    
    file_path = os.path.join(save_directory, secure_filename)
    if not validate_file_path(file_path, save_directory):
        raise HTTPException(status_code=400, detail="Invalid file path detected")
    
    # Save the file
    if storage_type == StorageType.FILE:
        os.makedirs(save_directory, exist_ok=True)
        try:
            # Double-check the path is absolute and within the expected directory
            abs_file_path = os.path.abspath(file_path)
            abs_save_dir = os.path.abspath(save_directory)
            
            if not abs_file_path.startswith(abs_save_dir):
                logger.error(f"Security check failed: {abs_file_path} is outside {abs_save_dir}")
                raise HTTPException(status_code=400, detail="Security violation: path would escape safe directory")
            
            with open(file_path, "wb") as f:
                contents = await file.read()
                f.write(contents)
                file.file.close()
            logger.info(f"File saved successfully to {file_path}")
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    elif storage_type == StorageType.S3:
        bucket_name = get_config("BUCKET_NAME")
        s3_file_path = f"resources/agent_{agent_id}/{secure_filename}"
        try:
            s3.upload_fileobj(file.file, bucket_name, s3_file_path)
            file_path = s3_file_path  # Store S3 path
            logger.info(f"File uploaded successfully to S3: {s3_file_path}")
        except NoCredentialsError:
            raise HTTPException(status_code=500, detail="AWS credentials not found. Check your configuration.")
        except Exception as e:
            logger.error(f"Error uploading to S3: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error uploading to S3: {str(e)}")

    # Create resource using original (sanitized) filename as display name
    resource = Resource(name=original_filename, path=file_path, storage_type=storage_type.value, 
                       size=size, type=type, channel="INPUT", agent_id=agent.id)

    db.session.add(resource)
    db.session.commit()
    db.session.flush()

    summarize_resource.delay(agent_id, resource.id)
    logger.info(f"Resource created: {resource.id} - {resource.name} - {resource.path}")

    return resource


@router.get("/get/all/{agent_id}", status_code=200)
def get_all_resources(agent_id: int,
                      Authorize: AuthJWT = Depends(check_auth)):
    """
    Get all resources for an agent.

    Args:
        agent_id (int): ID of the agent.

    Returns:
        List[Resource]: List of resources belonging to the agent.

    """

    resources = db.session.query(Resource).filter(Resource.agent_id == agent_id).all()
    return resources


@router.get("/get/{resource_id}", status_code=200)
def download_file_by_id(resource_id: int,
                        Authorize: AuthJWT = Depends(check_auth)):
    """
    Download a particular resource by resource_id.

    Args:
        resource_id (int): ID of the resource.
        Authorize (AuthJWT, optional): Authorization dependency.

    Returns:
        StreamingResponse: Streaming response for downloading the resource.

    Raises:
        HTTPException (status_code=400): If the resource with the specified ID is not found.
        HTTPException (status_code=404): If the file is not found.

    """

    resource = db.session.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    if not resource.agent_id:
        raise HTTPException(status_code=400, detail="Resource has no associated agent")
    
    agent = db.session.query(Agent).filter(Agent.id == resource.agent_id).first()
    if not agent:
        raise HTTPException(status_code=400, detail="Associated agent not found")
    
    stored_path = resource.path
    display_name = resource.name
    
    if '..' in stored_path or '~' in stored_path:
        logger.warning(f"Suspicious path detected: {stored_path}")
        raise HTTPException(status_code=403, detail="Access forbidden: Invalid path")
    
    if resource.storage_type == StorageType.S3.value:
        bucket_name = get_config("BUCKET_NAME")
        try:
            response = s3.get_object(Bucket=bucket_name, Key=stored_path)
            content = response["Body"]
            logger.info(f"File retrieved from S3: {stored_path}")
        except Exception as e:
            logger.error(f"Error retrieving from S3: {str(e)}")
            raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")
    else:
        try:
            base_directory = ResourceHelper.get_root_input_dir()
            if "{agent_id}" in base_directory:
                base_directory = ResourceHelper.get_formatted_agent_level_path(
                    agent=agent,
                    path=base_directory
                )
            
            abs_file_path = os.path.abspath(stored_path)
            
            if not validate_file_path(stored_path, base_directory):
                raise HTTPException(status_code=403, detail="Access forbidden: Invalid file path")
            
            if not os.path.isfile(abs_file_path):
                logger.error(f"File not found: {abs_file_path}")
                raise HTTPException(status_code=404, detail="File not found")
            
            filename = os.path.basename(abs_file_path)
            parts = filename.split('_', 2)
            if len(parts) < 3 or not parts[0].isdigit() or len(parts[1]) != 16:
                logger.warning(f"Incorrect file format: {filename}")
                raise HTTPException(status_code=403, detail="Access forbidden: Invalid file format")
            
            content = open(abs_file_path, "rb")
            logger.info(f"File retrieved from disk: {abs_file_path}")
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error accessing file: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

    return StreamingResponse(
        content,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={display_name}"
        }
    )
