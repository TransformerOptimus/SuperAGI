from fastapi import APIRouter, Depends, HTTPException
from superagi.helper.auth import check_auth
from superagi.helper.analytics_helper import AnalyticsHelper
from fastapi_jwt_auth import AuthJWT
from fastapi_sqlalchemy import db

router = APIRouter()

@router.get("/metrics", status_code=200)
def get_metrics(Authorize: AuthJWT = Depends(check_auth)):
    """
    Get the total tokens, total calls, and the number of run completed.

    Returns:
        metrics: dictionary containing total tokens, total calls, and the number of runs completed.

    """
    try:
        return AnalyticsHelper.calculate_run_completed_metrics(db.session)
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/agents/all", status_code=200)
def get_agents(Authorize: AuthJWT = Depends(check_auth)):
    try:
        return AnalyticsHelper.fetch_agent_data(db.session)
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")