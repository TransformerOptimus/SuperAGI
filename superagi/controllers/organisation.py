from fastapi import APIRouter
from fastapi import HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from fastapi_sqlalchemy import db
from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from superagi.helper.auth import check_auth
from superagi.helper.tool_helper import register_toolkits
from superagi.models.organisation import Organisation
from superagi.models.project import Project
from superagi.models.user import User
from superagi.lib.logger import logger

router = APIRouter()


# CRUD Operations
@router.post("/add", response_model=sqlalchemy_to_pydantic(Organisation), status_code=201)
def create_organisation(organisation: sqlalchemy_to_pydantic(Organisation, exclude=["id"]),
                        Authorize: AuthJWT = Depends(check_auth)):
    """
    Create a new organisation.

    Args:
        organisation: Organisation data.

    Returns:
        dict: Dictionary containing the created organisation.

    Raises:
        HTTPException (status_code=400): If there is an issue creating the organisation.

    """

    new_organisation = Organisation(
        name=organisation.name,
        description=organisation.description,
    )
    db.session.add(new_organisation)
    db.session.commit()
    db.session.flush()
    register_toolkits(session=db.session, organisation=new_organisation)
    logger.info(new_organisation)

    return new_organisation


@router.get("/get/{organisation_id}", response_model=sqlalchemy_to_pydantic(Organisation))
def get_organisation(organisation_id: int, Authorize: AuthJWT = Depends(check_auth)):
    """
    Get organisation details by organisation_id.

    Args:
        organisation_id: ID of the organisation.

    Returns:
        dict: Dictionary containing the organisation details.

    Raises:
        HTTPException (status_code=404): If the organisation with the specified ID is not found.

    """

    db_organisation = db.session.query(Organisation).filter(Organisation.id == organisation_id).first()
    if not db_organisation:
        raise HTTPException(status_code=404, detail="organisation not found")
    return db_organisation


@router.put("/update/{organisation_id}", response_model=sqlalchemy_to_pydantic(Organisation))
def update_organisation(organisation_id: int, organisation: sqlalchemy_to_pydantic(Organisation, exclude=["id"]),
                        Authorize: AuthJWT = Depends(check_auth)):
    """
    Update organisation details by organisation_id.

    Args:
        organisation_id: ID of the organisation.
        organisation: Updated organisation data.

    Returns:
        dict: Dictionary containing the updated organisation details.

    Raises:
        HTTPException (status_code=404): If the organisation with the specified ID is not found.

    """

    db_organisation = db.session.query(Organisation).filter(Organisation.id == organisation_id).first()
    if not db_organisation:
        raise HTTPException(status_code=404, detail="Organisation not found")

    db_organisation.name = organisation.name
    db_organisation.description = organisation.description
    db.session.commit()

    return db_organisation


@router.get("/get/user/{user_id}", response_model=sqlalchemy_to_pydantic(Organisation), status_code=201)
def get_organisations_by_user(user_id: int):
    """
    Get organisations associated with a user.If Organisation does not exists a new organisation is created

    Args:
        user_id: ID of the user.

    Returns:
        dict: Dictionary containing the organisation details.

    Raises:
        HTTPException (status_code=400): If the user with the specified ID is not found.

    """

    user = db.session.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=400,
                            detail="User not found")

    organisation = Organisation.find_or_create_organisation(db.session, user)
    Project.find_or_create_default_project(db.session, organisation.id)
    return organisation
