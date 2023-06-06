from fastapi import APIRouter
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from superagi.models.configuration import Configuration
from superagi.models.organisation import Organisation
from fastapi_sqlalchemy import db
from fastapi import HTTPException, Depends, Request
from superagi.config.config import get_config
from superagi.helper.auth import check_auth
from fastapi_jwt_auth import AuthJWT



router = APIRouter()


# CRUD Operations
@router.post("/add/organisation/{organisation_id}", status_code=201,response_model=sqlalchemy_to_pydantic(Configuration))
def create_config(config: sqlalchemy_to_pydantic(Configuration, exclude=["id"]),organisation_id:int,
                  Authorize: AuthJWT = Depends(check_auth)):

    """Create a new Organisation level config"""

    db_organisation = db.session.query(Organisation).filter(Organisation.id == organisation_id).first()
    if not db_organisation:
        raise HTTPException(status_code=404, detail="Organisation not found")

    existing_config = (
        db.session.query(Configuration)
        .filter(Configuration.organisation_id == config.organisation_id, Configuration.key == config.key)
        .first()
    )

    if existing_config:
        existing_config.value = config.value
        db.session.commit()
        db.session.flush()
        return existing_config

    new_config = Configuration(organisation_id=config.organisation_id, key=config.key, value=config.value)
    db.session.add(new_config)
    db.session.commit()
    db.session.flush()
    return new_config


@router.get("/get/organisation/{organisation_id}/key/{key}",
            response_model=sqlalchemy_to_pydantic(Configuration), status_code=201)
def create_config(organisation_id: int, key: str,
                  Authorize: AuthJWT = Depends(check_auth)):

    """Get Config from organisation_id and given key"""

    db_organisation = db.session.query(Organisation).filter(Organisation.id == organisation_id).first()
    if not db_organisation:
        raise HTTPException(status_code=404, detail="Organisation not found")

    config = db.session.query(Configuration).filter(Configuration.organisation_id == organisation_id, Configuration.key == key).first()

    return config


@router.get("/get/organisation/{organisation_id}", status_code=201)
def create_config(organisation_id: int,
                  Authorize: AuthJWT = Depends(check_auth)):

    """Get all configs from organisation_id"""

    db_organisation = db.session.query(Organisation).filter(Organisation.id == organisation_id).first()
    if not db_organisation:
        raise HTTPException(status_code=404, detail="Organisation not found")

    config = db.session.query(Configuration).filter(Configuration.organisation_id == organisation_id).all()
    return config


@router.get("/get/env", status_code=200)
def current_env():

    """Get current ENV"""

    env = get_config("ENV")
    return {
        "env": env
    }