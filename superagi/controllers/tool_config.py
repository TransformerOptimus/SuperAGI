from fastapi import APIRouter, HTTPException, Depends, Path
from fastapi_sqlalchemy import db
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from superagi.models.organisation import Organisation
from superagi.models.tool_config import ToolConfig
from superagi.models.tool_kit import ToolKit
from fastapi_jwt_auth import AuthJWT
from superagi.helper.auth import check_auth
from superagi.helper.auth import get_user_organisation
from typing import List

router = APIRouter()



# @router.post("/add/{tool_kit_name}", status_code=201, response_model=sqlalchemy_to_pydantic(ToolConfig))
# def create_or_update_tool_config(tool_kit_name: str, tool_config: sqlalchemy_to_pydantic(ToolConfig),
#                                  Authorize: AuthJWT = Depends(check_auth)):
#     """Create or update a Tool Configuration by Tool Kit Name"""
#
#     toolkit = db.session.query(ToolKit).filter_by(name=tool_kit_name).first()
#     if not toolkit:
#         raise HTTPException(status_code=404, detail='ToolKit not found')
#
#     existing_tool_config = db.session.query(ToolConfig).filter(
#         ToolConfig.tool_kit_id == toolkit.id,
#         ToolConfig.key == tool_config.key
#     ).first()
#
#     if existing_tool_config:
#         # Update the existing tool config
#         existing_tool_config.value = tool_config.value
#         db.session.commit()
#         db.session.refresh(existing_tool_config)
#         return existing_tool_config
#     else:
#         # Create a new tool config
#         new_tool_config = ToolConfig(**tool_config.dict())
#         db.session.add(new_tool_config)
#         db.session.commit()
#         db.session.refresh(new_tool_config)
#         return new_tool_config


@router.post("/add/{tool_kit_name}", status_code=201, response_model=sqlalchemy_to_pydantic(ToolConfig))
def create_or_update_tool_config(tool_kit_name: str, tool_configs,
                                 Authorize: AuthJWT = Depends(check_auth)):
    """Create or update Tool Configurations by Tool Kit Name"""

    toolkit = db.session.query(ToolKit).filter_by(name=tool_kit_name).first()
    if not toolkit:
        raise HTTPException(status_code=404, detail='ToolKit not found')

    # Iterate over the tool_configs list
    for tool_config_data in tool_configs:
        key = tool_config_data.key
        value = tool_config_data.value

        existing_tool_config = db.session.query(ToolConfig).filter(
            ToolConfig.tool_kit_id == toolkit.id,
            ToolConfig.key == key
        ).first()

        if existing_tool_config:
            # Update the existing tool config
            existing_tool_config.value = value
        else:
            # Create a new tool config
            new_tool_config = ToolConfig(key=key, value=value, tool_kit_id=toolkit.id)
            db.session.add(new_tool_config)

    db.session.commit()
    db.session.refresh(toolkit)

    return toolkit



@router.get("/get/toolkit/{tool_kit_name}", status_code=200)
def get_all_tool_configs(tool_kit_name: str, organisation: Organisation = Depends(get_user_organisation)):
    """Get all tool configurations by Tool Kit Name"""
    user_tool_kits = db.session.query(ToolKit).filter(ToolKit.organisation_id == organisation.id).all()

    toolkit = db.session.query(ToolKit).filter_by(name=tool_kit_name).first()
    if not toolkit:
        raise HTTPException(status_code=404, detail='ToolKit not found')

    if toolkit not in user_tool_kits:
        raise HTTPException(status_code=403, detail='Unauthorized')

    tool_configs = db.session.query(ToolConfig).filter(ToolConfig.organisation_id == organisation.id).all()

    return tool_configs


@router.get("/get/toolkit/{tool_kit_name}/key/{key}", status_code=200)
def get_tool_config(toolkit: str,key: str, organisation: Organisation = Depends(get_user_organisation)):
    """Get a specific tool configuration by org_id and key"""
    user_tool_kits = db.session.query(ToolKit).filter(ToolKit.organisation_id == organisation.id).all()

    toolkit = db.session.query(ToolKit).filter_by(name=toolkit)
    if toolkit not in user_tool_kits:
        raise HTTPException(status_code=403, detail='Unauthorized')

    tool_config = db.session.query(ToolConfig).filter(
        ToolConfig.tool_kit_id == toolkit.id,
        ToolConfig.key == key
    ).first()

    if not tool_config:
        raise HTTPException(status_code=404, detail="Tool configuration not found")

    return tool_config
