from fastapi import APIRouter, Depends, HTTPException
from superagi.helper.auth import check_auth, get_user_organisation
from superagi.helper.models_helper import ModelsHelper
from fastapi_jwt_auth import AuthJWT
from fastapi_sqlalchemy import db
import logging

router = APIRouter()

@router.get("/getModels", status_code=200)
def getModels(organisation=Depends(get_user_organisation)):
    try:
        return ModelsHelper(session=db.session, organisation_id=organisation.id).fetchModels()
    except Exception as e:
        logging.error(f"Error while fetching agent data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
