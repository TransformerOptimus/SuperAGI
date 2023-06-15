from fastapi import Depends, HTTPException
from fastapi_jwt_auth import AuthJWT

from superagi.config.config import get_config
from fastapi_sqlalchemy import db
from superagi.models.user import User
from superagi.models.organisation import Organisation


def check_auth(Authorize: AuthJWT = Depends()):
    env = get_config("ENV", "DEV")
    if env == "PROD":
        Authorize.jwt_required()
    return Authorize

# def authorize_user(Authorize: AuthJWT = Depends(check_auth)):
#     """Dependency function to authorize the user based on the JWT token"""
#
#     email = Authorize.get_jwt_subject()
#     user = db.session.query(User).filter(User.email == email).first()
#     if not user:
#         raise HTTPException(status_code=403, detail="Unauthorized")
#     return user

# def authorize_organisation(organisation_id: int, Authorize: AuthJWT = Depends(check_auth)):
#     """Dependency function to validate the organisation ID and check if the user has access"""
#
#     email = Authorize.get_jwt_subject()
#     user = db.session.query(User).filter(User.email == email).first()
#     if not user:
#         raise HTTPException(status_code=403, detail="Unauthorized")
#
#     organisation = db.session.query(Organisation).filter(Organisation.id == organisation_id).first()
#     if not organisation:
#         raise HTTPException(status_code=404, detail="Organisation not found")
#
#     # Check if the user has access to the organisation
#     if user.organisation_id != organisation_id:
#         raise HTTPException(status_code=403, detail="User does not have access to the organisation")
#
#     return organisation


def get_user_organisation(Authorize: AuthJWT = Depends(check_auth)):
    env = get_config("ENV", "DEV")

    if env == "DEV":
        email = "super6@agi.com"
    else:
        # Retrieve the email of the logged-in user from the JWT token payload
        email = Authorize.get_jwt_subject()

    # Query the User table to find the user by their email
    user = db.session.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401 ,detail="Unauthenticated")
    organisation = db.session.query(Organisation).filter(Organisation.id == user.organisation_id).first()
    return organisation
