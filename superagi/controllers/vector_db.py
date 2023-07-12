from fastapi_sqlalchemy import db
from fastapi import HTTPException, Depends
from fastapi import APIRouter
from superagi.config.config import get_config
from superagi.models.vector_db import Vectordb
from superagi.models.vector_db_config import VectordbConfig
from superagi.models.vector_db_index_collection import VectorIndexCollection
from superagi.models.index_config import VectorIndexConfig
from superagi.helper.pinecone_helper import PineconeHelper
from superagi.helper.qdrant_helper import QdrantHelper
from superagi.helper.auth import get_user_organisation
router = APIRouter()
@router.get("/get/list")
def handle_marketplace_operations_list():
    """
    Handle marketplace operation list.
    Args:
        page (int, optional): The page number for pagination. Defaults to None.
    Returns:
        dict: The response containing the marketplace list.
    """
    marketplace_organisation_id = int(get_config("MARKETPLACE_ORGANISATION_ID"))
    marketplace_vector_dbs = Vectordb.fetch_marketplace_list(db.session, marketplace_organisation_id)
    #marketplace_vector_dbs_with_install = Vectordb.get_vector_db_installed_details(db.session, marketplace_vector_dbs,
    #                                                                          organisation)
    return marketplace_vector_dbs
@router.post("/connect/pinecone")
def connect_pinecone_vector_db(data: dict, organisation = Depends(get_user_organisation)):
    for collection in data["collections"]:
        index_dimensions = PineconeHelper(db.session).get_dimensions(data["api_key"], data["environment"], collection)
        index_state = PineconeHelper(db.session).get_pinecone_index_state(data["api_key"], data["environment"], collection)
        if not index_dimensions["success"] or not index_state["success"]:
            return {"success": False}
        key_data = {
            "dimensions": index_dimensions["dimensions"],
            "index_state": index_state["state"]
        }
    pinecone_db = Vectordb.add_database(db.session, data["name"], "Pinecone", organisation)
    pinecone_keys = ["API_KEY", "ENVIRONMENT"]
    for key in pinecone_keys:
        VectordbConfig.add_database_config(db.session, pinecone_db.id, key.lower(), data[key.lower()])
    for collection in data["collections"]:
        vector_index = VectorIndexCollection.add_vector_index(db.session, collection, pinecone_db.id)
        for key in key_data.keys():
           VectorIndexConfig.add_vector_index_config(db.session, vector_index.id, key, key_data[key])
    return {"success": True, "id": pinecone_db.id, "name": pinecone_db.name}
@router.post("/connect/qdrant")
def connect_qdrant_vector_db(data: dict, organisation = Depends(get_user_organisation)):
    for collection in data["collections"]:
        index_dimensions = QdrantHelper(db.session).get_dimensions(data["api_key"], data["url"], data["port"], collection)
        index_state = PineconeHelper(db.session).get_pinecone_index_state(data["api_key"], data["url"], data["port"], collection)
        if not index_dimensions["success"] or not index_state["success"]:
            return {"success": False}
        key_data = {
            "dimensions": index_dimensions["dimensiosn"],
            "index_state": index_state["state"]
        }
    qdrant_db = Vectordb.add_database(db.session, data["name"], "Qdrant", organisation)
    qdrant_keys = ["API_KEY", "ENVIRONMENT"]
    for key in qdrant_keys:
        VectordbConfig.add_database_config(db.session, qdrant_db.id, key.lower(), data[key.lower()])
    for collection in data["collections"]:
        vector_index = VectorIndexCollection.add_vector_index(db.session, collection, qdrant_db.id)
        for key in key_data.keys():
           VectorIndexConfig.add_vector_index_config(db.session, vector_index.id, key, key_data[key])
    return {"success": True, "id": qdrant_db.id, "name": qdrant_db.name}
@router.get("/user/list")
def get_user_connected_vector_db(organisation = Depends(get_user_organisation)):
    vector_db_list = Vectordb.get_vector_db_organisation(db.session, organisation)
    return vector_db_list
@router.post("/update/vector_db/{vector_db_id}")
def update_vector_indices(new_indices: list, vector_db_id: int):
    vector_db = db.session.query(Vectordb).filter(Vectordb.id == vector_db_id).first()
    existing_index = VectorIndexCollection.get_vector_index_organisation(db.session, vector_db_id)
    existing_index_names = []
    for index in existing_index:
        if index.name not in new_indices:
            VectorIndexConfig.delete_vector_index_config(db.session, vector_index_id=index.id)
            VectorIndexCollection.delete_vector_index(db.session, id=index.id)
        existing_index_names.append(index.name)
    existing_indices_names = set(existing_index_names)
    new_indices_names = set(new_indices)
    added_indices = new_indices_names - existing_indices_names
    for index in added_indices:
        vector_index = VectorIndexCollection.add_vector_index(db.session, existing_index, vector_db_id)
        if vector_db.db_type == "Pinecone":
            api_key = db.session.query(VectordbConfig).filter(VectordbConfig.vector_db_id == vector_db_id, VectordbConfig.key == "api_key").first()
            environment = db.session.query(VectordbConfig).filter(VectordbConfig.vector_db_id == vector_db_id, VectordbConfig.key == "environment").first()
            index_dimensions = PineconeHelper(db.session).get_dimensions(api_key.value, environment.value, vector_index.name)
            index_state = PineconeHelper(db.session).get_pinecone_index_state(api_key.value, environment.value, vector_index.name)
        elif vector_db.db_type == "Qdrant":
            api_key = db.session.query(VectordbConfig).filter(VectordbConfig.vector_db_id == vector_db_id, VectordbConfig.key == "api_key").first()
            url = db.session.query(VectordbConfig).filter(VectordbConfig.vector_db_id == vector_db_id, VectordbConfig.key == "url").first()
            port = db.session.query(VectordbConfig).filter(VectordbConfig.vector_db_id == vector_db_id, VectordbConfig.key == "port").first()
            index_dimensions = QdrantHelper(db.session).get_dimensions(api_key.value, url.value, port.value, vector_index.name)
            index_state = QdrantHelper(db.session).get_qdrant_index_state(api_key.value, url.value, port.value, vector_index.name)
        if not index_dimensions["success"] or not index_state:
            return {"success": False}
        key_data = {
            "dimensions": index_dimensions["dimensions"],
            "index_state": index_state["state"]
        }
        for key in key_data.keys():
            VectorIndexConfig.add_vector_index_config(db.session, vector_index.id, key, key_data[key])
    return {"success": True}
@router.get("/get/db/details/{vector_db_id}")
def get_vector_db_details(vector_db_id: int):
    vector_db = db.session.query(Vectordb).filter(Vectordb.id == vector_db_id).first()
    vector_db_config = db.session.query(VectordbConfig).filter(VectordbConfig.vector_db_id == vector_db_id).all()
    vector_data = {
        "id": vector_db.id,
        "name": vector_db.name,
        "db_type": vector_db.db_type
    }
    for config in vector_db_config:
        vector_data[config.key.lower()] = config.value
    indices = db.session.query(VectorIndexCollection).filter(VectorIndexCollection.vector_db_id == vector_db.id).all()
    vector_indices = []
    for index in indices:
        vector_indices.append(index.name)
    vector_data["indices"] = vector_indices
    return vector_data
@router.post("/delete/{vector_db_id}")
def delete_vector_db(vector_db_id: int):
    vector_indices = VectorIndexCollection.get_vector_index_organisation(db.session, vector_db_id)
    for index in vector_indices:
        VectorIndexConfig.delete_vector_index_config(db.session, vector_index_id=index.id)
        VectorIndexCollection.delete_vector_index(db.session, id=index.id)
    VectordbConfig.delete_vector_db_config(db.session, vector_db_id=vector_db_id)
    Vectordb.delete_vector_db(db.session, vector_db_id=vector_db_id)