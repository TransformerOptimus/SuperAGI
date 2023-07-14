from fastapi_sqlalchemy import db
from fastapi import HTTPException, Depends
from fastapi import APIRouter
from superagi.config.config import get_config
from superagi.models.vector_dbs import Vectordbs
from superagi.helper.auth import get_user_organisation
from superagi.models.vector_db_configs import VectordbConfigs
from superagi.models.vector_db_indices import VectordbIndices

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
    return vector_db_list

@router.get("/get/db/details/{vector_db_id}")
def get_vector_db_details(vector_db_id: int):
    vector_db = Vectordbs.get_vector_db_from_id(vector_db_id)
    vector_db_data = {
        "id": vector_db.id,
        "name": vector_db.name,
        "db_type": vector_db.db_type
    }
    vector_db_config = VectordbConfigs.get_vector_db_config_from_db_id(db.session, vector_db_id)
    vector_db_with_config = vector_db | vector_db_config
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
            VectordbIndices.delete_vector_db_index(db.session, vector_index.id)
        VectordbConfigs.delete_vector_db_configs(db.session, vector_db_id)
        Vectordbs.delete_vector_db(db.session, vector_db_id)
    except:
        raise HTTPException(status_code=404, detail="VectorDb not found")

