from fastapi import Depends
from fastapi_jwt_auth import AuthJWT

from superagi.config.config import get_config


def check_auth(Authorize: AuthJWT = Depends()):
    env = get_config("ENV", "DEV")
    if env == "PROD":
        Authorize.jwt_required()
