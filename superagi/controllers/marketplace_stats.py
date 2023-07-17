from fastapi_sqlalchemy import db
from fastapi import HTTPException, Depends, Query, status
from fastapi import APIRouter
from superagi.config.config import get_config
from superagi.models.marketplace_stats import MarketPlaceStats
from superagi.models.vector_dbs import Vectordbs

router = APIRouter()

@router.get("/knowledge/downloads/{knowledge_id}")
def get_knowledge_download_number(knowledge_id: int):
    marketplace_organisation_id = int(get_config("MARKETPLACE_ORGANISATION_ID"))
    download_number = db.session.query(MarketPlaceStats).filter(MarketPlaceStats.reference_id, MarketPlaceStats.reference_name == "KNOWLEDGE", MarketPlaceStats.key == "download_count").first()
    if download_number is None:
        downlods = 0
    else:
        downlods = download_number.value
    return downlods
