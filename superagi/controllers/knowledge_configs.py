from fastapi_sqlalchemy import db
from fastapi import HTTPException, Depends, Query, status
from fastapi import APIRouter
from superagi.config.config import get_config
from superagi.helper.auth import get_user_organisation
from superagi.models.knowledge_configs import KnowledgeConfigs

router = APIRouter()

@router.get("/marketplace/details/{knowledge_id}")
def get_marketplace_knowledge_configs_details(knowledge_id: int):
    print("///////////////////////")
    print(knowledge_id)
    knowledge_configs = db.session.query(KnowledgeConfigs).filter(KnowledgeConfigs.knowledge_id == knowledge_id).all()
    print("////////////////////////////")
    print(knowledge_configs)
    return knowledge_configs