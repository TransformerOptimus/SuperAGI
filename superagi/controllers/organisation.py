from fastapi_sqlalchemy import DBSessionMiddleware, db
from fastapi import HTTPException, Depends, Request
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from superagi.models.organisation import Organisation
from fastapi import APIRouter
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from superagi.helper.auth import check_auth
from superagi.models.project import Project
from superagi.models.user import User

router = APIRouter()


# CRUD Operations
@router.post("/add",     response_model=sqlalchemy_to_pydantic(Organisation), status_code=201)
def create_organisation(organisation: sqlalchemy_to_pydantic(Organisation, exclude=["id"]),
                        Authorize: AuthJWT = Depends(check_auth)):
    """Create a new organistaion"""

    new_organisation = Organisation(
            name=organisation.name,
        description=organisation.description,
    )
    db.session.add(new_organisation)
    db.session.commit()
    db.session.flush()
    print(new_organisation)

    return new_organisation


@router.get("/get/{organisation_id}", response_model=sqlalchemy_to_pydantic(Organisation))
def get_organisation(organisation_id: int, Authorize: AuthJWT = Depends(check_auth)):
    """Get Organistaion details by organistaion_id"""
    db_organisation = db.session.query(Organisation).filter(Organisation.id == organisation_id).first()
    if not db_organisation:
        raise HTTPException(status_code=404, detail="organisation not found")
    return db_organisation


@router.put("/update/{organisation_id}", response_model=sqlalchemy_to_pydantic(Organisation))
def update_organisation(organisation_id: int, organisation: sqlalchemy_to_pydantic(Organisation, exclude=["id"]),
                        Authorize: AuthJWT = Depends(check_auth)):
    """Update organistaion details by organistaion_id"""

    db_organisation = db.session.query(Organisation).filter(Organisation.id == organisation_id).first()
    if not db_organisation:
        raise HTTPException(status_code=404, detail="Organisation not found")

    db_organisation.name = organisation.name
    db_organisation.description = organisation.description
    db.session.commit()

    return db_organisation

@router.get("/get/user/{user_id}",response_model=sqlalchemy_to_pydantic(Organisation), status_code=201)
def get_organisations_by_user(user_id: int):
    user = db.session.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=400,
                            detail="User not found")

    organisation = Organisation.find_or_create_organisation(db.session, user)
    Project.find_or_create_default_project(db.session, organisation.id)
    return organisation
