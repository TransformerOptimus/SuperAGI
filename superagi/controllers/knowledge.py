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
from superagi.helper.pinecone_helper import PineconeHelper
from superagi.helper.qdrant_helper import QdrantHelper
from superagi.helper.knowledge_helper import KnowledgeHelper
from superagi.models.vector_db_config import VectordbConfig
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
        knowledge["install_number"] = MarketPlaceStats.get_knowledge_installation_number(db.session, knowledge["id"])
    return marketplace_knowledges_with_install

@router.get("/user/list")
def get_user_knowledge_list(Authorize: AuthJWT = Depends(), organisation = Depends(get_user_organisation)):
    organisation_id = organisation.id
    marketplace_organisation_id = int(get_config("MARKETPLACE_ORGANISATION_ID"))
    user_knowledge_list = Knowledge.get_user_knowledge_list(db.session, organisation_id)
    for user_knowledge in user_knowledge_list:
        user_knowledge["is_marketplace"] = Knowledge.check_if_marketplace(db.session, user_knowledge, marketplace_organisation_id)    
    return user_knowledge_list

@router.get("/marketplace/get/details/{knowledge_id}")
def get_knowledge_details(knowledge_id: int):
    knowledge_data = db.session.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
    knowledge = {
        "name": knowledge_data.name,
        "descriptiom": knowledge_data.description,
        "readme": knowledge_data.readme,
        "contributed_by": knowledge_data.contributed_by,
        "updated_at": knowledge_data.updated_at
    }
    knowledge_with_config = KnowledgeConfig.get_knowledge_config(db.session, knowledge_id, knowledge)
    knowledge_with_config["install_number"] = MarketPlaceStats.get_knowledge_installation_number(db.session, knowledge_id)
    return knowledge_with_config

@router.get("/user/get/details/{knowledge_id}")
def get_user_knowledge_details(knowledge_id: int):
    marketplace_organisation_id = int(get_config("MARKETPLACE_ORGANISATION_ID"))
    knowledge_data = db.session.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
    vector_database_index = VectorIndexCollection.get_vector_index_from_id(db.session, knowledge_data.index_id)
    vector_database = Vectordb.get_vector_db_from_id(db.session, vector_database_index.vector_db_id)
    knowledge = {
        "name": knowledge_data.name,
        "description": knowledge_data.description,
        "vector_database_index": {
            "id": vector_database_index.id,
            "name": vector_database_index.name
        },
        "vector_database": vector_database.name
    }
    is_installed = Knowledge.check_if_marketplace(db.session, knowledge, marketplace_organisation_id)
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
    knowledge_data["summary"] = summary["content"]
    knowledge_data["organisation_id"] = organisation.id
    knowledge_data["contributed_by"] = organisation.name
    knowledge = Knowledge.add_update_knowledge(db.session, knowledge_data)
    return {"success": True, "id": knowledge.id}

@router.post("/delete/{knowledge_id}")
def delete_knowledge(knowledge_id: int):
    db.session.query(Knowledge).filter(Knowledge.id == knowledge_id).delete()
    db.session.commit()
    return {"success": True}

@router.post("/install/{knowledge_id}/index/{index_id}")
def install_selected_knowledge(knowledge_id: int, index_id: int, organisation = Depends(get_user_organisation)):
    index = db.session.query(VectorIndexCollection).filter(VectorIndexCollection.id == index_id).first()
    file_path = db.session.query(KnowledgeConfig).filter(KnowledgeConfig.knowledge_id == knowledge_id, KnowledgeConfig.key == "file_path").first()
    chunk_data = KnowledgeHelper(db.session).get_json_from_s3(file_path)
    if index.db_type == "Pinecone":
        api_key = db.session.query(VectordbConfig).filter(VectordbConfig.vector_db_id == index.vector_db_id, VectordbConfig.key == "api_key").first()
        environment = db.session.query(VectordbConfig).filter(VectordbConfig.vector_db_id == index.vector_db_id, VectordbConfig.key == "environment").first()
        pinecone_helper = PineconeHelper(db.session, api_key.value, environment.value)
        upsert_data = pinecone_helper.get_upsert_data(chunk_data)
        installed_knowledge = pinecone_helper.install_pinecone_knowledge(index, upsert_data)

    elif index.db_type == "Qdrant":
        api_key = db.session.query(VectordbConfig).filter(VectordbConfig.vector_db_id == index.vector_db_id, VectordbConfig.key == "api_key").first()
        url = db.session.query(VectordbConfig).filter(VectordbConfig.vector_db_id == index.vector_db_id, VectordbConfig.key == "url").first()
        port = db.session.query(VectordbConfig).filter(VectordbConfig.vector_db_id == index.vector_db_id, VectordbConfig.key == "port").first()
        qdrant_helper = QdrantHelper(db.session, api_key.value, url.value, port.value)
        upsert_data = qdrant_helper.get_upsert_data(chunk_data)
        installed_knowledge = qdrant_helper.install_qdrant_knowledge(index, upsert_data)
    
    if not installed_knowledge["success"]:
        return {"success": False}
    
    selected_knoweldge = Knowledge.get_knowledge_from_id(db.session, knowledge_id)
    selected_knowledge_data = {
        "name": selected_knoweldge.name,
        "description": selected_knoweldge.description,
        "summary": selected_knoweldge.summary,
        "readme": selected_knoweldge.readme,
        "index_id": index_id,
        "organisation_id": organisation.id,
        "contributed_by": selected_knoweldge.contributed_by
    }
    new_knowledge = Knowledge.add_update_knowledge(db.session, selected_knowledge_data)
    selected_knowledge_config = KnowledgeConfig.get_knowledge_config(db.session, knowledge_id, {})
    selected_knowledge_config.pop("file_path")
    KnowledgeConfig.add_knowledge_config(db.session, new_knowledge.id, selected_knowledge_config)
    return {"success": True}

@router.post("/uninstall/{knowledge_id}")
def uninstall_selected_knowledge(knowledge_id: int):
    knowledge = db.session.query(Knowledge).filter(Knowledge.id == knowledge_id).first()
    vector_ids = db.session.query(KnowledgeConfig).filter(KnowledgeConfig.knowledge_id == knowledge_id, KnowledgeConfig.key == "vector_ids").first()
    vector_ids = list(vector_ids.value)
    index = db.session.query(VectorIndexCollection).filter(VectorIndexCollection.id == knowledge.index_id).first()
    if index.db_type == "Pinecone":
        api_key = db.session.query(VectordbConfig).filter(VectordbConfig.vector_db_id == index.vector_db_id, VectordbConfig.key == "api_key").first()
        environment = db.session.query(VectordbConfig).filter(VectordbConfig.vector_db_id == index.vector_db_id, VectordbConfig.key == "environment").first()
        pinecone_helper = PineconeHelper(db.session, api_key.value, environment.value)
        deleted_knowledge = pinecone_helper.uninstall_pinecone_knowledge(index, vector_ids)
    
    elif index.db_type == "Qdrant":
        api_key = db.session.query(VectordbConfig).filter(VectordbConfig.vector_db_id == index.vector_db_id, VectordbConfig.key == "api_key").first()
        url = db.session.query(VectordbConfig).filter(VectordbConfig.vector_db_id == index.vector_db_id, VectordbConfig.key == "url").first()
        port = db.session.query(VectordbConfig).filter(VectordbConfig.vector_db_id == index.vector_db_id, VectordbConfig.key == "port").first()
        qdrant_helper = QdrantHelper(db.session, api_key.value, url.value, port.value)
        deleted_knowledge = qdrant_helper.uninstall_qdrant_knowledge(index, vector_ids)
    
    if not deleted_knowledge["success"]:
        return {"success": False}
    
    else:
        db.session.query(KnowledgeConfig).filter(KnowledgeConfig.knowledge_id == knowledge_id).delete()
        db.session.commit()
        db.session.query(Knowledge).filter(Knowledge.id == knowledge_id).delete()
        db.session.commit()
    return {"success": True}
        