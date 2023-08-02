from datetime import datetime
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from superagi.models.configuration import Configuration
from superagi.models.organisation import Organisation
from fastapi_sqlalchemy import db
from fastapi import HTTPException, Depends, Request
from superagi.config.config import get_config
from superagi.helper.auth import check_auth
from fastapi_jwt_auth import AuthJWT
from superagi.helper.encyption_helper import encrypt_data,decrypt_data
from superagi.lib.logger import logger
# from superagi.types.db import ConfigurationIn, ConfigurationOut

router = APIRouter()


class ConfigurationOut(BaseModel):
    id: int
    organisation_id: int
    key: str
    value: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ConfigurationIn(BaseModel):
    organisation_id: Optional[int]
    key: str
    value: str

    class Config:
        orm_mode = True

# CRUD Operations
@router.post("/add/organisation/{organisation_id}", status_code=201,
             response_model=ConfigurationOut)
def create_config(config: ConfigurationIn, organisation_id: int,
                  Authorize: AuthJWT = Depends(check_auth)):
    """
    Creates a new Organisation level config.

    Args:
        config (Configuration): Configuration details.
        organisation_id (int): ID of the organisation.

    Returns:
        Configuration: Created configuration.

    """

    db_organisation = db.session.query(Organisation).filter(Organisation.id == organisation_id).first()
    if not db_organisation:
        raise HTTPException(status_code=404, detail="Organisation not found")

    existing_config = (
        db.session.query(Configuration)
        .filter(Configuration.organisation_id == organisation_id, Configuration.key == config.key)
        .first()
    )

    # Encrypt the API key
    if config.key == "model_api_key":
        encrypted_value = encrypt_data(config.value)
        config.value = encrypted_value

    if existing_config:
        existing_config.value = config.value
        db.session.commit()
        db.session.flush()
        return existing_config

    logger.info("NEW CONFIG")
    new_config = Configuration(organisation_id=organisation_id, key=config.key, value=config.value)
    logger.info(new_config)
    logger.info("ORGANISATION ID : ", organisation_id)
    db.session.add(new_config)
    db.session.commit()
    db.session.flush()
    return new_config


@router.get("/get/organisation/{organisation_id}/key/{key}", status_code=200)
def get_config_by_organisation_id_and_key(organisation_id: int, key: str,
                                          Authorize: AuthJWT = Depends(check_auth)):
    """
    Get a configuration by organisation ID and key.

    Args:
        organisation_id (int): ID of the organisation.
        key (str): Key of the configuration.
        Authorize (AuthJWT, optional): Authorization JWT token. Defaults to Depends(check_auth).

    Returns:
        Configuration: Retrieved configuration.

    """

    db_organisation = db.session.query(Organisation).filter(Organisation.id == organisation_id).first()
    if not db_organisation:
        raise HTTPException(status_code=404, detail="Organisation not found")

    config = db.session.query(Configuration).filter(Configuration.organisation_id == organisation_id,
                                                    Configuration.key == key).first()
    if config is None and key == "model_api_key":
        api_key = get_config("OPENAI_API_KEY") or get_config("PALM_API_KEY")
        if (api_key is not None and api_key != "YOUR_OPEN_API_KEY") or (
                api_key is not None and api_key != "YOUR_PALM_API_KEY"):
            encrypted_data = encrypt_data(api_key)
            new_config = Configuration(organisation_id=organisation_id, key="model_api_key",value=encrypted_data)
            db.session.add(new_config)
            db.session.commit()
            db.session.flush()
            return new_config
        return config

    # Decrypt the API key
    if config is not None and config.key == "model_api_key":
        if config.value is not None:
            decrypted_data = decrypt_data(config.value)
            config.value = decrypted_data

    return config


@router.get("/get/organisation/{organisation_id}", status_code=201)
def get_config_by_organisation_id(organisation_id: int,
                                  Authorize: AuthJWT = Depends(check_auth)):
    """
    Get all configurations for a given organisation ID.

    Args:
        organisation_id (int): ID of the organisation.
        Authorize (AuthJWT, optional): Authorization JWT token. Defaults to Depends(check_auth).

    Returns:
        List[Configuration]: List of configurations for the organisation.

    """

    db_organisation = db.session.query(Organisation).filter(Organisation.id == organisation_id).first()
    if not db_organisation:
        raise HTTPException(status_code=404, detail="Organisation not found")

    configs = db.session.query(Configuration).filter(Configuration.organisation_id == organisation_id).all()

    # Decrypt the API key if the key is "model_api_key"
    for config in configs:
        if config.key == "model_api_key":
            decrypted_value = decrypt_data(config.value)
            config.value = decrypted_value

    return configs


@router.get("/get/env", status_code=200)
def current_env():
    """
    Get the current environment.

    Returns:
        dict: Dictionary containing the current environment.

    """

    env = get_config("ENV", "DEV")
    return {
        "env": env
    }
