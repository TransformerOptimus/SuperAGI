from fastapi_sqlalchemy import db
from fastapi import HTTPException, Depends
from fastapi import APIRouter
from superagi.config.config import get_config
from datetime import datetime
from superagi.helper.time_helper import get_time_difference
from superagi.models.vector_dbs import Vectordbs
from superagi.helper.auth import get_user_organisation
from superagi.models.vector_db_configs import VectordbConfigs
from superagi.models.vector_db_indices import VectordbIndices
from superagi.vector_store.vector_factory import VectorFactory
from superagi.models.knowledges import Knowledges

router = APIRouter()

@router.get("/get/list")
def get_vector_db_list():
    marketplace_vector_dbs = Vectordbs.fetch_marketplace_list()
    return marketplace_vector_dbs

@router.get("/marketplace/list")
def get_marketplace_vectordb_list():
    organisation_id = int(get_config("MARKETPLACE_ORGANISATION_ID"))
    vector_dbs = db.session.query(Vectordbs).filter(Vectordbs.organisation_id == organisation_id).all()
    return vector_dbs

@router.get("/user/list")
def get_user_connected_vector_db_list(organisation = Depends(get_user_organisation)):
    vector_db_list = Vectordbs.get_vector_db_from_organisation(db.session, organisation)
    if vector_db_list:
        for vector in vector_db_list:
            vector.updated_at = get_time_difference(vector.updated_at, str(datetime.now()))
    return vector_db_list

@router.get("/db/details/{vector_db_id}")
def get_vector_db_details(vector_db_id: int):
    vector_db = Vectordbs.get_vector_db_from_id(db.session, vector_db_id)
    vector_db_data = {
        "id": vector_db.id,
        "name": vector_db.name,
        "db_type": vector_db.db_type
    }
    vector_db_config = VectordbConfigs.get_vector_db_config_from_db_id(db.session, vector_db_id)
    vector_db_with_config = vector_db_data | vector_db_config
    indices = db.session.query(VectordbIndices).filter(VectordbIndices.vector_db_id == vector_db_id).all()
    vector_indices = []
    for index in indices:
        vector_indices.append(index.name)
    vector_db_with_config["indices"] = vector_indices
    return vector_db_with_config

@router.post("/delete/{vector_db_id}")
def delete_vector_db(vector_db_id: int):
    try:
        vector_indices = VectordbIndices.get_vector_indices_from_vectordb(db.session, vector_db_id)
        for vector_index in vector_indices:
            Knowledges.delete_knowledge_from_vector_index(db.session, vector_index.id)
            VectordbIndices.delete_vector_db_index(db.session, vector_index.id)
        VectordbConfigs.delete_vector_db_configs(db.session, vector_db_id)
        Vectordbs.delete_vector_db(db.session, vector_db_id)
    except:
        raise HTTPException(status_code=404, detail="VectorDb not found")
    
@router.post("/connect/pinecone")
def connect_pinecone_vector_db(data: dict, organisation = Depends(get_user_organisation)):
    db_creds = {
        "api_key": data["api_key"],
        "environment": data["environment"]
    }
    for collection in data["collections"]:
        try:
            vector_db_storage = VectorFactory.build_vector_storage("pinecone", collection, **db_creds)
            db_connect_for_index = vector_db_storage.get_index_stats()
            index_state = "Custom" if db_connect_for_index["vector_count"] > 0 else "None"
        except:
            raise HTTPException(status_code=400, detail="Unable to connect Pinecone")
    pinecone_db = Vectordbs.add_vector_db(db.session, data["name"], "Pinecone", organisation)
    VectordbConfigs.add_vector_db_config(db.session, pinecone_db.id, db_creds)
    for collection in data["collections"]:
        VectordbIndices.add_vector_index(db.session, collection, pinecone_db.id, db_connect_for_index["dimensions"], index_state)
    return {"id": pinecone_db.id, "name": pinecone_db.name}

@router.post("/connect/qdrant")
def connect_qdrant_vector_db(data: dict, organisation = Depends(get_user_organisation)):
    db_creds = {
        "api_key": data["api_key"],
        "url": data["url"],
        "port": data["port"]
    }
    for collection in data["collections"]:
        try:
            vector_db_storage = VectorFactory.build_vector_storage("qdrant", collection, **db_creds)
            db_connect_for_index = vector_db_storage.get_index_stats()
            index_state = "Custom" if db_connect_for_index["vector_count"] > 0 else "None"
        except:
            raise HTTPException(status_code=400, detail="Unable to connect Qdrant")
    qdrant_db = Vectordbs.add_vector_db(db.session, data["name"], "Qdrant", organisation)
    VectordbConfigs.add_vector_db_config(db.session, qdrant_db.id, db_creds)
    for collection in data["collections"]:
        VectordbIndices.add_vector_index(db.session, collection, qdrant_db.id, db_connect_for_index["dimensions"], index_state)
    
    return {"id": qdrant_db.id, "name": qdrant_db.name}

@router.put("/update/vector_db/{vector_db_id}")
def update_vector_db(new_indices: list, vector_db_id: int):
    vector_db = Vectordbs.get_vector_db_from_id(db.session, vector_db_id)
    existing_indices = VectordbIndices.get_vector_indices_from_vectordb(db.session, vector_db_id)
    existing_index_names = []
    for index in existing_indices:
        if index.name not in new_indices:
            VectordbIndices.delete_vector_db_index(db.session, vector_index_id=index.id)
        existing_index_names.append(index.name)
    existing_index_names = set(existing_index_names)
    new_indices_names = set(new_indices)
    added_indices = new_indices_names - existing_index_names
    for index in added_indices:
        db_creds = VectordbConfigs.get_vector_db_config_from_db_id(db.session, vector_db_id)
        try:
            vector_db_storage  = VectorFactory.build_vector_storage(vector_db.db_type, index, **db_creds)
            vector_db_index_stats = vector_db_storage.get_index_stats()
            index_state = "Custom" if vector_db_index_stats["vector_count"] > 0 else "None"
        except:
           raise HTTPException(status_code=400, detail="Unable to update vector db")
        VectordbIndices.add_vector_index(db.session, index, vector_db_id, vector_db_index_stats["dimensions"], index_state)



        