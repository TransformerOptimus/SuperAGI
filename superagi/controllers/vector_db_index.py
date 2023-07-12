from fastapi_sqlalchemy import db
from fastapi import HTTPException, Depends, Query
from fastapi import APIRouter
from superagi.models.vector_db import Vectordb
from superagi.models.vector_db_config import VectordbConfig
from superagi.models.vector_db_index_collection import VectorIndexCollection
from superagi.models.index_config import VectorIndexConfig
from superagi.helper.knowledge_helper import KnowledgeHelper
from superagi.helper.auth import get_user_organisation

router = APIRouter()

@router.get("/get/marketplace/valid_indices/{knowledge_id}")
def get_marketplace_valid_indices(knowledge_id: int, organisation = Depends(get_user_organisation)):
    vector_dbs = Vectordb.get_vector_db_organisation(db.session, organisation)
    pinecone = []
    qdrant = []
    for vector in vector_dbs:
        indices = db.session.query(VectorIndexCollection).filter(VectorIndexCollection.vector_db_id == vector["id"]).all()
        for index in indices:
            data = {
                "id": index.id,
                "name": index.name 
            }
            data["is_valid_dimension"] = KnowledgeHelper(db.session).check_valid_dimension(data["id"], knowledge_id)
            state = VectorIndexConfig.get_index_state(db.session, data["id"])
            if state != "CUSTOM":
                data["is_valid_state"] = True
            if vector["db_type"] == "Pinecone":
                pinecone.append(data)
            elif vector["db_type"] == "Qdrant":
                qdrant.append(data)
    vector_indices_data = {
        "pinecone": pinecone,
        "qdrant": qdrant
    }
    
    return vector_indices_data

@router.get("/get/user/valid_indices")
def get_user_valid_indices(organisation = Depends(get_user_organisation)):
    vector_dbs = Vectordb.get_vector_db_organisation(db.session, organisation)
    pinecone = []
    qdrant = []
    for vector in vector_dbs:
        indices = db.session.query(VectorIndexCollection).filter(VectorIndexCollection.vector_db_id == vector["id"]).all()
        for index in indices:
            data = {
                "id": index.id,
                "name": index.name
            }
            state = VectorIndexConfig.get_index_state(db.session, data["id"])
            if state == "CUSTOM":
                data["is_valid_state"] = True
            if vector["db_type"] == "Pinecone":
                pinecone.append(data)
            elif vector["db_type"] == "Qdrant":
                qdrant.append(data)
    vector_indices_data = {
        "pinecone": pinecone,
        "qdrant": qdrant
    }
    
    return vector_indices_data
