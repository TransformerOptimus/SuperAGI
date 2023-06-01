from fastapi_sqlalchemy import DBSessionMiddleware, db
from fastapi import HTTPException, Depends, Request
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from superagi.models.budget import Budget
from fastapi import APIRouter, UploadFile
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
import os
from fastapi import FastAPI, File, Form, UploadFile
from typing import Annotated
from superagi.models.resource import Resource
from superagi.config.config import get_config
from superagi.models.project import Project
from starlette.responses import FileResponse
from pathlib import Path
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.post("/add/{project_id}", status_code=201)
async def upload(project_id: int, file: UploadFile = File(...), name=Form(...), size=Form(...), type=Form(...)):
    project = db.session.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=400, detail="Project does not exists")

    if not name.endswith(".txt") and not name.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File type not supported!")

    storage_type = get_config("STORAGE_TYPE")
    save_directory = get_config("RESOURCES_INPUT_ROOT_DIR")

    path = ""
    if storage_type == "FILE":
        os.makedirs(save_directory, exist_ok=True)
        # Create the file path
        file_path = os.path.join(save_directory, file.filename)
        # Save the file to the specified directory
        path = file_path
        with open(file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)
            file.file.close()
    elif storage_type == "S3":
        # Logic for uploading to S3
        bucket_name = get_config("BUCKET_NAME")
        s3_key = get_config("S3_KEY")
        # path to be added
        pass

    resource = Resource(name=name, path=path, storage_type=storage_type, size=size, type=type, channel="INPUT",
                        project_id=project.id)
    db.session.add(resource)
    db.session.commit()
    db.session.flush()
    print(resource)
    return resource


@router.get("/get/all/{project_id}", status_code=200)
def get_all_resources(project_id: int):
    resources = db.session.query(Resource).filter(Resource.project_id == project_id).all()
    return resources


@router.get("/get/{resource_id}", status_code=200)
def download_file_by_id(resource_id: int):
    resource = db.session.query(Resource).filter(Resource.id == resource_id).first()
    download_file_path = resource.path
    file_name = resource.name

    if not resource:
        raise HTTPException(status_code=400, detail="Resource Not found!")

    abs_file_path = Path(download_file_path).resolve()
    if not abs_file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return StreamingResponse(
        open(str(abs_file_path), "rb"),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={file_name}"
        }
    )
