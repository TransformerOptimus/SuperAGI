from fastapi_sqlalchemy import db
from fastapi import HTTPException, Depends, Request
from fastapi_jwt_auth import AuthJWT

from superagi.models.organisation import Organisation
from superagi.models.project import Project
from superagi.models.user import User
from fastapi import APIRouter
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from superagi.helper.auth import check_auth

router = APIRouter()


# CRUD Operations
@router.post("/add", response_model=sqlalchemy_to_pydantic(User), status_code=201)
def create_user(user: sqlalchemy_to_pydantic(User, exclude=["id"]),
                Authorize: AuthJWT = Depends(check_auth)):
    db_user = db.session.query(User).filter(User.email == user.email).first()
    if db_user:
        return db_user
    db_user = User(name=user.name, email=user.email, password=user.password, organisation_id=user.organisation_id)
    db.session.add(db_user)
    db.session.commit()
    db.session.flush()
    organisation = Organisation.find_or_create_organisation(db.session, db_user)
    Project.find_or_create_default_project(db.session, organisation.id)
    print("User created", db_user)
    return db_user


@router.get("/get/{user_id}", response_model=sqlalchemy_to_pydantic(User))
def get_user(user_id: int,
             Authorize: AuthJWT = Depends(check_auth)):
    # Authorize.jwt_required()
    db_user = db.session.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/update/{user_id}", response_model=sqlalchemy_to_pydantic(User))
def update_user(user_id: int,
                user: sqlalchemy_to_pydantic(User, exclude=["id"]),
                Authorize: AuthJWT = Depends(check_auth)):
    db_user = db.session.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.name = user.name
    db_user.email = user.email
    db_user.password = user.password

    db.session.commit()
    return db_user
