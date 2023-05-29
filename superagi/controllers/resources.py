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


router = APIRouter()


# CRUD Operations
@router.post("/add", status_code=201)
def upload(file: UploadFile = File(...)):
    try:
        save_directory = "./uploaded_files"
        # Create the save directory if it doesn't exist
        os.makedirs(save_directory, exist_ok=True)
        # Create the file path
        file_path = os.path.join(save_directory, file.filename)
        # Save the file to the specified directory
        with open(file_path, "wb") as f:
            contents = file.read()
            f.write(contents)
        # async with aiofiles.open(file_path, "wb") as f:
        #     contents = await file.read()
        #     await f.write(contents)


    except Exception:
        print(Exception)
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    return {"message": f"Successfully uploaded {file.filename}"}
# async def create_upload_file(file: Annotated[bytes, File()]):
#     return {"filename": file.filename}

# async def create_file(
#     file: Annotated[bytes, File()],
#     fileb: Annotated[UploadFile, File()],
#     token: Annotated[str, Form()],
# ):
#     return {
#         "file_size": len(file),
#         "token": token,
#         "fileb_content_type": fileb.content_type,
#     }
#
# def upload_file(file: UploadFile = UploadFile(...)):
#     save_directory = "./uploaded_files"
#
#     # Create the save directory if it doesn't exist
#     os.makedirs(save_directory, exist_ok=True)
#
#     # Create the file path
#     file_path = os.path.join(save_directory, file.filename)
#
#     # Save the file to the specified directory
#     with open(file_path, "wb") as f:
#         contents = file.read()
#         f.write(contents)
#
#     return {"filename": file.filename, "saved_path": file_path}
