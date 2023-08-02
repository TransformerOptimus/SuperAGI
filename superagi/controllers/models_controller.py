from fastapi import APIRouter, Depends, HTTPException
from superagi.helper.auth import check_auth, get_user_organisation
from superagi.helper.models_helper import ModelsHelper
from fastapi_jwt_auth import AuthJWT
from fastapi_sqlalchemy import db
import logging
from pydantic import BaseModel

router = APIRouter()

class ValidateAPIKeyRequest(BaseModel):
    model_provider: str
    model_api_key: str

@router.post("/storeApiKeys")
async def storeApiKeys(request: ValidateAPIKeyRequest, organisation=Depends(get_user_organisation)):
    try:
        model_provider = request.model_provider
        model_api_key = request.model_api_key
        return ModelsHelper(session=db.session, organisation_id=organisation.id).storeApiKey(model_provider, model_api_key)
    except Exception as e:
        logging.error(f"Error while storing API key: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
