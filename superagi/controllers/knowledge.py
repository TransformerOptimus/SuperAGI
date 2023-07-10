from fastapi_sqlalchemy import db
from fastapi import HTTPException, Depends, Query, status
from fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter
from superagi.config.config import get_config
from superagi.helper.auth import get_user_organisation
from superagi.models.knowledge import Knowledge
from superagi.models.knowledge_config import KnowledgeConfig
from superagi.models.vector_db_index_collection import VectorIndexCollection
from superagi.models.vector_db import Vectordb
from superagi.models.marketplace_stats import MarketPlaceStats
from superagi.llms.openai import OpenAi
from superagi.helper.auth import get_user_organisation

router = APIRouter()


@router.get("/get/list")
def handle_marketplace_operations_list(
        page: int = Query(None, title="Page Number"),
        organisation = Depends(get_user_organisation)
):
    """
    Handle marketplace operation list.

    Args:
        page (int, optional): The page number for pagination. Defaults to None.

    Returns:
        dict: The response containing the marketplace list.

    """

    marketplace_organisation_id = int(get_config("MARKETPLACE_ORGANISATION_ID"))
    marketplace_knowledges = Knowledge.fetch_marketplace_list(db.session, page, marketplace_organisation_id)
    marketplace_knowledges_with_install = Knowledge.get_knowledge_installed_details(db.session, marketplace_knowledges,
                                                                              organisation)
    for knowledge in marketplace_knowledges_with_install:
        knowledge["install_number"] = MarketPlaceStats.get_knowledge_installation_number(db.session, knowledge.id)
    return marketplace_knowledges_with_install

@router.get("/user/list")
def get_user_knowledge_list(Authorize: AuthJWT = Depends(), organisation = Depends(get_user_organisation)):
    organisation_id = organisation.id
    marketplace_organisation_id = int(get_config("MARKETPLACE_ORGANISATION_ID"))
    user_knowledge_list = Knowledge.get_user_knowledge_list(organisation_id)
    for user_knowledge in user_knowledge_list:
        user_knowledge["is_marketplace"] = Knowledge.check_if_marketplace(db.session, user_knowledge, marketplace_organisation_id)    
    return user_knowledge_list

@router.get("/get/user/list")
def user_accessible_knowledge_list(organisation = Depends(get_user_organisation)):
    knowledge_list = db.session.query(Knowledge).filter(Knowledge.organisation_id == organisation.id)    
    return knowledge_list

@router.get("/marketplace/get/details/{knowledge_id}")
def get_knowledge_details(knowledge_id: int):
    knowledge_data = db.session.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
    knowledge = {
        "name": knowledge_data.name,
        "descriptiom": knowledge_data.description,
        "readme": knowledge_data.readme,
        "contributed_by": knowledge_data.contributed_by,
    }
    knowledge_with_config = KnowledgeConfig.get_knowledge_config(db.session, knowledge_id, knowledge)
    knowledge_with_config["install_number"] = MarketPlaceStats.get_knowledge_installation_number(db.session, knowledge_id)
    return knowledge_with_config

@router.get("/user/get/details/{knowledge_id}")
def get_user_knowledge_details(knowledge_id: int, organisation = Depends(get_user_organisation)):
    marketplace_organisation_id = int(get_config("MARKETPLACE_ORGANISATION_ID"))
    knowledge_data = db.session.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
    vector_database_index = VectorIndexCollection.get_vector_index_from_id(db.session, knowledge_data.index_id)
    vector_database = Vectordb.get_vector_db_from_id(db.session, vector_database_index.vector_db_id)
    knowledge = {
        "name": knowledge_data.name,
        "description": knowledge_data.description,
        "vector_database_index": vector_database_index.name,
        "vector_database": vector_database.name
    }
    is_installed = Knowledge.check_if_marketplace(db.session, knowledge_data, marketplace_organisation_id, knowledge)
    if is_installed:
        knowledge["installation_type"] = "Marketplace"
    else:
        knowledge["installation_type"] = "Custom"
    knowledge_with_config = KnowledgeConfig.get_knowledge_config(db.session, knowledge_id, knowledge)
    return knowledge_with_config

@router.post("/add_or_update/data")
def add_new_user_knowledge(knowledge_data: dict, organisation = Depends(get_user_organisation)):
    try:
        llm = OpenAi(api_key=get_config("OPENAI_API_KEY"))
        message = [{"role": "system", "content": "You are a helpful assistant that helps in content writing and summarising the information as precise and short as possible in not more than 100 words."},
                   {"role": "user", "content": knowledge_data["description"]}]
        summary = llm.chat_completion(messages=message)
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    knowledge_data["summary"] = summary
    knowledge_data["organisation_id"] = organisation.id
    knowledge_data["contributed_by"] = organisation.name
    Knowledge.add_update_knowledge(db.session, knowledge_data)
    return {"success": True}

@router.post("/delete/{knowledge_id}")
def delete_knowledge(knowledge_id: int):
    db.session.query(Knowledge).filter(Knowledge.id == knowledge_id).delete()
    db.session.commit()
    return {"success": True}