from fastapi import APIRouter, Depends, HTTPException, Query, Body
from superagi.helper.auth import check_auth, get_user_organisation
from superagi.helper.models_helper import ModelsHelper
from superagi.apm.call_log_helper import CallLogHelper
from superagi.models.models import Models
from superagi.models.models_config import ModelsConfig
from superagi.config.config import get_config
from superagi.controllers.types.models_types import ModelsTypes
from fastapi_sqlalchemy import db
import logging
from pydantic import BaseModel

router = APIRouter()


class ValidateAPIKeyRequest(BaseModel):
    model_provider: str
    model_api_key: str


class StoreModelRequest(BaseModel):
    model_name: str
    description: str
    end_point: str
    model_provider_id: int
    token_limit: int
    type: str
    version: str

class ModelName (BaseModel):
    model: str

@router.post("/store_api_keys", status_code=200)
async def store_api_keys(request: ValidateAPIKeyRequest, organisation=Depends(get_user_organisation)):
    try:
        return ModelsConfig.store_api_key(db.session, organisation.id, request.model_provider, request.model_api_key)
    except Exception as e:
        logging.error(f"Error while storing API key: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/get_api_keys")
async def get_api_keys(organisation=Depends(get_user_organisation)):
    try:
        return ModelsConfig.fetch_api_keys(db.session, organisation.id)
    except Exception as e:
        logging.error(f"Error while retrieving API Keys: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/get_api_key", status_code=200)
async def get_api_key(model_provider: str = None, organisation=Depends(get_user_organisation)):
    try:
        return ModelsConfig.fetch_api_key(db.session, organisation.id, model_provider)
    except Exception as e:
        logging.error(f"Error while retrieving API Key: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/verify_end_point", status_code=200)
async def verify_end_point(model_api_key: str = None, end_point: str = None, model_provider: str = None):
    try:
        return ModelsHelper.validate_end_point(model_api_key, end_point, model_provider)
    except Exception as e:
        logging.error(f"Error validating Endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/store_model", status_code=200)
async def store_model(request: StoreModelRequest, organisation=Depends(get_user_organisation)):
    try:
        return Models.store_model_details(db.session, organisation.id, request.model_name, request.description, request.end_point, request.model_provider_id, request.token_limit, request.type, request.version)
    except Exception as e:
        logging.error(f"Error storing the Model Details: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/fetch_models", status_code=200)
async def fetch_models(organisation=Depends(get_user_organisation)):
    try:
        return Models.fetch_models(db.session, organisation.id,)
    except Exception as e:
        logging.error(f"Error Fetching Models: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/fetch_model/{model_id}", status_code=200)
async def fetch_model_details(model_id: int, organisation=Depends(get_user_organisation)):
    try:
        return Models.fetch_model_details(db.session, organisation.id, model_id)
    except Exception as e:
        logging.error(f"Error Fetching Model Details: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/fetch_model_data", status_code=200)
async def fetch_data(request: ModelName, organisation=Depends(get_user_organisation)):
    try:
        return CallLogHelper(session=db.session, organisation_id=organisation.id).fetch_data(request.model)
    except Exception as e:
        logging.error(f"Error Fetching Model Details: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/get/list", status_code=200)
def get_knowledge_list(page: int = 0, organisation=Depends(get_user_organisation)):
    """
    Get Marketplace Model list.

    Args:
        page (int, optional): The page number for pagination. Defaults to None.

    Returns:
        dict: The response containing the marketplace list.

    """
    if page < 0:
        page = 0
    marketplace_models = Models.fetch_marketplace_list(page)
    marketplace_models_with_install = Models.get_model_install_details(db.session, marketplace_models, organisation.id)
    return marketplace_models_with_install


@router.get("/marketplace/list/{page}", status_code=200)
def get_marketplace_knowledge_list(page: int = 0):
    organisation_id = get_config("MARKETPLACE_ORGANISATION_ID")
    if organisation_id is not None:
        organisation_id = int(organisation_id)
    page_size = 16

    query = db.session.query(Models).filter(Models.org_id == organisation_id)
    if page < 0:
        models = query.all()
    models = query.offset(page * page_size).limit(page_size).all()
    return models


@router.get("/get/models_details", status_code=200)
def get_models_details(page: int = 0):
    """
        Get Marketplace Model list.

        Args:
            page (int, optional): The page number for pagination. Defaults to None.

        Returns:
            dict: The response containing the marketplace list.

        """
    organisation_id = get_config("MARKETPLACE_ORGANISATION_ID")
    if organisation_id is not None:
        organisation_id = int(organisation_id)

    if page < 0:
        page = 0
    marketplace_models = Models.fetch_marketplace_list(page)
    marketplace_models_with_install = Models.get_model_install_details(db.session, marketplace_models, organisation_id,
                                                                       ModelsTypes.MARKETPLACE.value)
    return marketplace_models_with_install