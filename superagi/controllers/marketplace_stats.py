from fastapi import APIRouter
from fastapi_sqlalchemy import db

from superagi.models.marketplace_stats import MarketPlaceStats

router = APIRouter()


@router.get("/knowledge/downloads/{knowledge_id}")
def count_knowledge_downloads(knowledge_id: int):
    download_number = (
        db.session.query(MarketPlaceStats)
        .filter(
            MarketPlaceStats.reference_id == knowledge_id,
            MarketPlaceStats.reference_name == "KNOWLEDGE",
            MarketPlaceStats.key == "download_count",
        )
        .first()
    )
    if download_number is None:
        downloads = 0
    else:
        downloads = download_number.value
    return downloads
