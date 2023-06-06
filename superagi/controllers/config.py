from fastapi import APIRouter
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from superagi.models.configuration import Configuration
from superagi.models.organisation import Organisation
from fastapi_sqlalchemy import db
from fastapi import HTTPException, Depends, Request
from superagi.config.config import get_config


router = APIRouter()


# CRUD Operations
@router.post("/add", status_code=201,)
def create_config(config: sqlalchemy_to_pydantic(Configuration, exclude=["id"])):

    """Create a new Organisation level config"""
    print("ADDING")
    print(config)

    new_config = Configuration(organisation_id=config.organisation_id, key=config.key, value=config.value)

    print(new_config)
    db.session.add(new_config)
    db.session.commit()
    db.session.flush()
    return new_config


@router.get("/get/organisation/{organisation_id}/key/{key}",
            response_model=sqlalchemy_to_pydantic(Configuration), status_code=201)
def create_config(organisation_id: int, key: int):

    """Get Config from organisation_id and given key"""

    db_organisation = db.session.query(Organisation).filter(Organisation.id == organisation_id).first()
    if not db_organisation:
        raise HTTPException(status_code=404, detail="Organisation not found")

    config = db.session.query(Configuration).filter(Configuration.organisation_id == organisation_id, Configuration.key == key).first()

    return config


@router.get("/get/organisation/{organisation_id}",
            response_model=sqlalchemy_to_pydantic(Configuration), status_code=201)
def create_config(organisation_id: int, key: int):

    """Get all configs from organisation_id"""

    db_organisation = db.session.query(Organisation).filter(Organisation.id == organisation_id).first()
    if not db_organisation:
        raise HTTPException(status_code=404, detail="Organisation not found")

    config = db.session.query(Configuration).filter(Configuration.organisation_id == organisation_id).first()
    return config


@router.get("/get/env", status_code=200)
def current_env():

    """Get current ENV"""

    env = get_config("ENV")
    return {
        "env": env
    }