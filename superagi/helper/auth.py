from fastapi import Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from fastapi_sqlalchemy import db

from superagi.config.config import get_config
from superagi.models.organisation import Organisation
from superagi.models.user import User


def check_auth(Authorize: AuthJWT = Depends()):
    """
    Function to check if the user is authenticated or not based on the environment.

    Args:
        Authorize (AuthJWT, optional): Instance of AuthJWT class to authorize the user. Defaults to Depends().

    Returns:
        AuthJWT: Instance of AuthJWT class if the user is authenticated.
    """
    env = get_config("ENV", "DEV")
    if env == "PROD":
        Authorize.jwt_required()
    return Authorize


def get_user_organisation(Authorize: AuthJWT = Depends(check_auth)):
    """
    Function to get the organisation of the authenticated user based on the environment.

    Args:
        Authorize (AuthJWT, optional): Instance of AuthJWT class to authorize the user. Defaults to Depends on check_auth().

    Returns:
        Organisation: Instance of Organisation class to which the authenticated user belongs.
    """
    user = get_current_user(Authorize)
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthenticated")
    organisation = db.session.query(Organisation).filter(Organisation.id == user.organisation_id).first()
    return organisation

def get_current_user(Authorize: AuthJWT = Depends(check_auth)):
    env = get_config("ENV", "DEV")

    if env == "DEV":
        email = "super6@agi.com"
    else:
        # Retrieve the email of the logged-in user from the JWT token payload
        email = Authorize.get_jwt_subject()

    # Query the User table to find the user by their email
    user = db.session.query(User).filter(User.email == email).first()
    return user