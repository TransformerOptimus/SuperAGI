from fastapi import APIRouter
from fastapi_sqlalchemy import db

from superagi.models.knowledge_configs import KnowledgeConfigs

router = APIRouter()


@router.get("/marketplace/details/{knowledge_id}")
def get_marketplace_knowledge_configs(knowledge_id: int):
    knowledge_configs = (
        db.session.query(KnowledgeConfigs)
        .filter(KnowledgeConfigs.knowledge_id == knowledge_id)
        .all()
    )
    return knowledge_configs
