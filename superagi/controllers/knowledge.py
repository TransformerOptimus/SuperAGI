from fastapi_sqlalchemy import db
from fastapi import HTTPException, Depends, Query
from fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter
from superagi.config.config import get_config
from superagi.helper.auth import get_user_organisation
from superagi.models.knowledge import Knowledge
from superagi.models.knowledge_config import KnowledgeConfig
from superagi.models.marketplace_stats import MarketPlaceStats
from superagi.helper.auth import get_user_organisation

router = APIRouter()


@router.get("/get/list/{page}")
def handle_marketplace_operations_list(
        page: int,
        organisation = Depends(get_user_organisation)
):
    """
    Handle marketplace operation list.

    Args:
        page (int, optional): The page number for pagination. Defaults to None.

    Returns:
        dict: The response containing the marketplace list.

    """

    marketplace_knowledges = Knowledge.fetch_marketplace_list(page=page)
    marketplace_knowledges_with_install = Knowledge.get_knowledge_installed_details(db.session, marketplace_knowledges,
                                                                              organisation)
    for knowledge in marketplace_knowledges_with_install:
        knowledge["install_number"] = MarketPlaceStats.get_knowledge_installation_number(db.session, knowledge.id)
    return marketplace_knowledges_with_install


#For internal use
@router.get("/marketplace/list/{page}")
def get_marketplace_knowledge(
        page: int = 0,
):
    """
    Get marketplace knowledges.

    Args:
        page (int): The page number for pagination.

    Returns:
        list: A list of knowledges.

    """

    organisation_id = int(get_config("MARKETPLACE_ORGANISATION_ID"))
    page_size = 30

    # Apply search filter if provided
    query = db.session.query(Knowledge).filter(Knowledge.organisation_id == organisation_id)

    # Paginate the results
    knowledges = query.offset(page * page_size).limit(page_size).all()


    return knowledges

@router.get("/user/list")
def get_user_knowledge_list(Authorize: AuthJWT = Depends(), organisation = Depends(get_user_organisation)):
    organisation_id = organisation.id
    marketplace_organisation_id = int(get_config("MARKETPLACE_ORGANISATION_ID"))
    user_knowledge_list = Knowledge.get_user_knowledge_list(organisation_id)
    for user_knowledge in user_knowledge_list:
        user_knowledge["is_marketplace"] = Knowledge.check_if_marketplace(db.session, user_knowledge, marketplace_organisation_id)    
    return user_knowledge_list

@router.get("get/user/list")
def user_accessible_knowledge_list(organisation_id):
    knowledge_list = db.session.query(Knowledge).filter(Knowledge.organisation_id == organisation_id)    
    return knowledge_list

@router.get("marketplace/get/details/{knowledge_id}")
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

@router.get("user/get/details/{knowledge_id}")
def get_user_knowledge_details(knowledge_id: int, organisation = Depends(get_user_organisation)):
    marketplace_organisation_id = int(get_config("MARKETPLACE_ORGANISATION_ID"))
    knowledge_data = db.session.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
    knowledge = {
        "name": knowledge_data.name,
        "description": knowledge_data.description
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
    summary = ""
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