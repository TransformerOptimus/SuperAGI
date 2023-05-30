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

router = APIRouter()


@router.post("/add", status_code=201)
async def upload(file: UploadFile = File(...), storage_type=Form(...), path=Form(...)):
    # try:
        save_directory = "./workspace/input"
        # # Create the save directory if it doesn't exist
        os.makedirs(save_directory, exist_ok=True)
        # Create the file path
        file_path = os.path.join(save_directory, file.filename)
        # Save the file to the specified directory
        with open(file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)

        if storage_type not in ["S3", "FILE"]:
            raise HTTPException(status_code=400, detail="S3,FILE are only supported storage type")
        if storage_type == "FILES":
            path = save_directory
        elif path is None:
            raise HTTPException(status_code=400, detail="S3 requires a path")

        resource = Resource(name=file.filename, path=path, storage_type=storage_type)
        db.session.add(resource)
        db.session.commit()

    # except Exception as error:
    #     print("ERROR!!")
    #     print(str(error))
        # raise HTTPException(status_code=500,detail="There was error uploading file")
    # finally:
        file.file.close()

        return resource

@router.get("/get/all", status_code=200)
def get_all_resources():
    resources = db.session.query(Resource).all()
    return resources
