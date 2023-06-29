from datetime import datetime
from typing import Optional

from fastapi_sqlalchemy import db
from fastapi import HTTPException, Depends, Request
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel

from superagi.models.organisation import Organisation
from superagi.models.project import Project
from superagi.models.user import User
from fastapi import APIRouter

from superagi.helper.auth import check_auth
from superagi.lib.logger import logger
# from superagi.types.db import UserBase, UserIn, UserOut

router = APIRouter()

class UserBase(BaseModel):
    name: str
    email: str
    password: str

    class Config:
        orm_mode = True


class UserOut(UserBase):
    id: int
    organisation_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class UserIn(UserBase):
    organisation_id: Optional[int]

    class Config:
        orm_mode = True

# CRUD Operations
@router.post("/add", response_model=UserOut, status_code=201)
def create_user(user: UserIn,
                Authorize: AuthJWT = Depends(check_auth)):
    """
    Create a new user.

    Args:
        user (UserIn): User data.

    Returns:
        User: The created user.

    Raises:
        HTTPException (status_code=400): If there is an issue creating the user.

    """

    db_user = db.session.query(User).filter(User.email == user.email).first()
    if db_user:
        return db_user
    db_user = User(name=user.name, email=user.email, password=user.password, organisation_id=user.organisation_id)
    db.session.add(db_user)
    db.session.commit()
    db.session.flush()
    organisation = Organisation.find_or_create_organisation(db.session, db_user)
    Project.find_or_create_default_project(db.session, organisation.id)
    logger.info("User created", db_user)
    return db_user


@router.get("/get/{user_id}", response_model=UserOut)
def get_user(user_id: int,
             Authorize: AuthJWT = Depends(check_auth)):
    """
    Get a particular user details.

    Args:
        user_id (int): ID of the user.

    Returns:
        User: The user details.

    Raises:
        HTTPException (status_code=404): If the user with the specified ID is not found.

    """

    # Authorize.jwt_required()
    db_user = db.session.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/update/{user_id}", response_model=UserOut)
def update_user(user_id: int,
                user: UserBase,
                Authorize: AuthJWT = Depends(check_auth)):
    """
    Update a particular user.

    Args:
        user_id (int): ID of the user.
        user (UserIn): Updated user data.

    Returns:
        User: The updated user details.

    Raises:
        HTTPException (status_code=404): If the user with the specified ID is not found.

    """

    db_user = db.session.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.name = user.name
    db_user.email = user.email
    db_user.password = user.password

    db.session.commit()
    return db_user
