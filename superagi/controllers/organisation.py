from fastapi_sqlalchemy import DBSessionMiddleware, db
from fastapi import HTTPException, Depends, Request
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from superagi.models.organisation import Organisation
from fastapi import APIRouter
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

router = APIRouter()


# CRUD Operations
@router.post("/add", response_model=sqlalchemy_to_pydantic(Organisation), status_code=201)
def create_organisation(organisation: sqlalchemy_to_pydantic(Organisation, exclude=["id"]),
                        Authorize: AuthJWT = Depends()):
    new_organisation = Organisation(
        name=organisation.name,
        description=organisation.description,
    )
    db.session.add(new_organisation)
    db.session.commit()

    return new_organisation


@router.get("/get/{organisation_id}", response_model=sqlalchemy_to_pydantic(Organisation))
def get_organisation(organisation_id: int, Authorize: AuthJWT = Depends()):
    db_organisation = db.session.query(Organisation).filter(Organisation.id == organisation_id).first()
    if not db_organisation:
        raise HTTPException(status_code=404, detail="organisation not found")
    return db_organisation


@router.put("/update/{organisation_id}", response_model=sqlalchemy_to_pydantic(Organisation))
def update_organisation(organisation_id: int, organisation: sqlalchemy_to_pydantic(Organisation, exclude=["id"]),
                        Authorize: AuthJWT = Depends()):
    db_organisation = db.session.query(Organisation).filter(Organisation.id == organisation_id).first()
    if not db_organisation:
        raise HTTPException(status_code=404, detail="Organisation not found")

    db_organisation.name = organisation.name
    db_organisation.description = organisation.description
    db.session.commit()

    return db_organisation
