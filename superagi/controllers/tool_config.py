from fastapi import APIRouter, HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from fastapi_sqlalchemy import db
from pydantic import BaseModel

from superagi.helper.auth import check_auth
from superagi.helper.auth import get_user_organisation
from superagi.models.organisation import Organisation
from superagi.models.tool_config import ToolConfig
from superagi.models.toolkit import Toolkit
from superagi.helper.encyption_helper import encrypt_data
from superagi.helper.encyption_helper import decrypt_data, is_encrypted
from superagi.types.key_type import ToolConfigKeyType
import json

router = APIRouter()

class ToolConfigOut(BaseModel):
    id = int
    key = str
    value = str
    toolkit_id = int

    class Config:
        orm_mode = True

@router.post("/add/{toolkit_name}", status_code=201)
def update_tool_config(toolkit_name: str, configs: list, organisation: Organisation = Depends(get_user_organisation)):
    """
    Update tool configurations for a specific tool kit.

    Args:
        toolkit_name (str): The name of the tool kit.
        configs (list): A list of dictionaries containing the tool configurations.
            Each dictionary should have the following keys:
            - "key" (str): The key of the configuration.
            - "value" (str): The new value for the configuration.

    Returns:
        dict: A dictionary with the message "Tool configs updated successfully".

    Raises:
        HTTPException (status_code=404): If the specified tool kit is not found.
        HTTPException (status_code=500): If an unexpected error occurs during the update process.
    """

    try:
        # Check if the tool kit exists
        toolkit = Toolkit.get_toolkit_from_name(db.session, toolkit_name,organisation)
        if toolkit is None:
            raise HTTPException(status_code=404, detail="Tool kit not found")

        # Update existing tool configs
        for config in configs:
            key = config.get("key")
            value = config.get("value")
            if value is None: 
                continue
            if key is not None:
                tool_config = db.session.query(ToolConfig).filter_by(toolkit_id=toolkit.id, key=key).first()
                if tool_config:
                    if tool_config.key_type ==  ToolConfigKeyType.FILE.value:
                        value = json.dumps(value)
                    # Update existing tool config
                    # added encryption
                    tool_config.value = encrypt_data(value)
                    db.session.commit()

        return {"message": "Tool configs updated successfully"}

    except Exception as e:
        # db.session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-or-update/{toolkit_name}", status_code=201, response_model=ToolConfigOut)
def create_or_update_tool_config(toolkit_name: str, tool_configs,
                                 Authorize: AuthJWT = Depends(check_auth)):
    """
    Create or update tool configurations for a specific tool kit.

    Args:
        toolkit_name (str): The name of the tool kit.
        tool_configs (list): A list of tool configuration objects.

    Returns:
        Toolkit: The updated tool kit object.

    Raises:
        HTTPException (status_code=404): If the specified tool kit is not found.
    """
    toolkit = db.session.query(Toolkit).filter_by(name=toolkit_name).first()
    if not toolkit:
        raise HTTPException(status_code=404, detail='ToolKit not found')

    # Iterate over the tool_configs list
    for tool_config in tool_configs:
        existing_tool_config = db.session.query(ToolConfig).filter(
            ToolConfig.toolkit_id == toolkit.id,
            ToolConfig.key == tool_config.key
        ).first()

        if existing_tool_config.value:
            # Update the existing tool config
            if existing_tool_config.key_type == ToolConfigKeyType.FILE.value:
                existing_tool_config.value = json.dumps(existing_tool_config.value)
            existing_tool_config.value = encrypt_data(tool_config.value)
        else:
            # Create a new tool config
            new_tool_config = ToolConfig(key=tool_config.key, value=encrypt_data(tool_config.value), toolkit_id=toolkit.id)
            db.session.add(new_tool_config)
    

    db.session.commit()
    db.session.refresh(toolkit)

    return toolkit


@router.get("/get/toolkit/{toolkit_name}", status_code=200)
def get_all_tool_configs(toolkit_name: str, organisation: Organisation = Depends(get_user_organisation)):
    """
    Get all tool configurations by Tool Kit Name.

    Args:
        toolkit_name (str): The name of the tool kit.
        organisation (Organisation): The organization associated with the user.

    Returns:
        list: A list of tool configurations for the specified tool kit.

    Raises:
        HTTPException (status_code=404): If the specified tool kit is not found.
        HTTPException (status_code=403): If the user is not authorized to access the tool kit.
    """

    toolkit = db.session.query(Toolkit).filter(Toolkit.name == toolkit_name,
                                               Toolkit.organisation_id == organisation.id).first()
    
    if not toolkit:
        raise HTTPException(status_code=404, detail='ToolKit not found')

    tool_configs = db.session.query(ToolConfig).filter(ToolConfig.toolkit_id == toolkit.id).all()
    for tool_config in tool_configs:
        if tool_config.value:
            if(is_encrypted(tool_config.value)):
                tool_config.value = decrypt_data(tool_config.value)
            if tool_config.key_type == ToolConfigKeyType.FILE.value:
                tool_config.value = json.loads(tool_config.value)
    
    return tool_configs


@router.get("/get/toolkit/{toolkit_name}/key/{key}", status_code=200)
def get_tool_config(toolkit_name: str, key: str, organisation: Organisation = Depends(get_user_organisation)):
    """
    Get a specific tool configuration by tool kit name and key.

    Args:
        toolkit_name (str): The name of the tool kit.
        key (str): The key of the tool configuration.
        organisation (Organisation): The organization associated with the user.

    Returns:
        ToolConfig: The tool configuration with the specified key.

    Raises:
        HTTPException (status_code=403): If the user is not authorized to access the tool kit.
        HTTPException (status_code=404): If the specified tool kit or tool configuration is not found.
    """

    user_toolkits = db.session.query(Toolkit).filter(Toolkit.organisation_id == organisation.id).all()

    toolkit = db.session.query(Toolkit).filter_by(name=toolkit_name)
    if toolkit not in user_toolkits:
        raise HTTPException(status_code=403, detail='Unauthorized')

    tool_config = db.session.query(ToolConfig).filter(
        ToolConfig.toolkit_id == toolkit.id,
        ToolConfig.key == key
    ).first()
    if not tool_config:
        raise HTTPException(status_code=404, detail="Tool configuration not found")
    if(is_encrypted(tool_config.value)):
        tool_config.value = decrypt_data(tool_config.value)
    if tool_config.key_type == ToolConfigKeyType.FILE.value:
        tool_config.value = json.loads(tool_config.value)

    return tool_config
