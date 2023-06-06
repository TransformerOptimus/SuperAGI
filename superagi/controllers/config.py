from fastapi import APIRouter
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from superagi.models.config import Config
from superagi.models.organisation import Organisation
from fastapi_sqlalchemy import db
from fastapi import HTTPException, Depends, Request
from superagi.config.config import get_config

router = APIRouter()


# CRUD Operations
@router.post("/add", response_model=sqlalchemy_to_pydantic(Config), status_code=201)
def create_config(config):

    """Create a new Organisation level config"""

    new_config = Config(organisation_id=config.organisation_id, key=config.key, value=config.value)
    db.session.add(new_config)
    db.session.commit()
    db.session.flush()
    return new_config


@router.get("/get/organisation/{organisation_id}/key/{key}",
             response_model=sqlalchemy_to_pydantic(Config), status_code=201)
def create_config(organisation_id: int, key: int):

    """Get Config from organisation_id and given key"""

    db_organisation = db.session.query(Organisation).filter(Organisation.id == organisation_id).first()
    if not db_organisation:
        raise HTTPException(status_code=404, detail="Organisation not found")

    config = db.session.query(Config).filter(Config.organisation_id == organisation_id, Config.key == key).first()

    return config


@router.get("/get/organisation/{organisation_id}",
             response_model=sqlalchemy_to_pydantic(Config), status_code=201)
def create_config(organisation_id: int, key: int):

    """Get all configs from organisation_id"""

    db_organisation = db.session.query(Organisation).filter(Organisation.id == organisation_id).first()
    if not db_organisation:
        raise HTTPException(status_code=404, detail="Organisation not found")

    config = db.session.query(Config).filter(Config.organisation_id == organisation_id).first()
    return config


@router.get("/get/env", status_code=200)
def current_env():

    """Get current ENV"""

    env = get_config("ENV")
    return {
        "env": env
    }