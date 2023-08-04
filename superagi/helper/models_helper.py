from typing import List, Dict, Union, Any
from sqlalchemy import text, func, and_
from sqlalchemy.orm import Session
from superagi.models.models_config import ModelsConfig
from superagi.models.models import Models
from superagi.llms.hugging_face import HuggingFace
from fastapi import HTTPException
import requests
import logging

class ModelsHelper:

    def __init__(self, session:Session, organisation_id: int):
        self.session = session
        self.organisation_id = organisation_id

    def storeApiKey(self, model_provider, model_api_key):
        existing_entry = self.session.query(ModelsConfig).filter(and_(ModelsConfig.org_id == self.organisation_id, ModelsConfig.source_name == model_provider)).first()

        if existing_entry:
            existing_entry.api_key = model_api_key
        else:
            new_entry = ModelsConfig(org_id=self.organisation_id, source_name=model_provider, api_key=model_api_key)
            self.session.add(new_entry)

        self.session.commit()

        return {'message': 'The API key was successfully stored'}


    def fetchApiKeys(self):
        api_key_info = self.session.query(ModelsConfig.source_name, ModelsConfig.api_key).filter(ModelsConfig.org_id == self.organisation_id).all()

        if not api_key_info:
            logging.error("No API key found for the provided model provider")
            return []

        api_keys = [{"source_name": source_name, "api_key": api_key} for source_name, api_key in api_key_info]

        return api_keys


    def fetchApiKey(self, model_provider):
        api_key_data = self.session.query(ModelsConfig.id, ModelsConfig.source_name, ModelsConfig.api_key).filter(and_(ModelsConfig.org_id == self.organisation_id, ModelsConfig.source_name == model_provider)).first()

        if api_key_data is None:
            return []
        else:
            api_key = [{'id': api_key_data.id,'source_name': api_key_data.source_name,'api_key': api_key_data.api_key}]
            return api_key


    def validateEndPoint(self, model_api_key, end_point, model_provider):
        result = {}
        if(model_provider == 'Hugging Face'):
            try:
                result = HuggingFace(api_key=model_api_key,end_point=end_point).get_model()
            except Exception as e:
                result = {'error': str(e)}

        if 'error' in result:
            return result['error']

        return result

    def storeModelDetails(self, model_name, description, end_point, model_provider_id, token_limit):
        if not model_name:
            return {"error": "Model Name is empty or undefined"}
        if not description:
            return {"error": "Description is empty or undefined"}
        if not end_point:
            return {"error": "End Point is empty or undefined"}
        if not model_provider_id:
            return {"error": "Model Provider Id is null or undefined or 0"}
        if not token_limit:
            return {"error": "Token Limit is null or undefined or 0"}

        try:
            model = Models(
                    model_name=model_name,
                    description=description,
                    end_point=end_point,
                    token_limit=token_limit,
                    model_provider_id=model_provider_id,
                    org_id=self.organisation_id
                )
            self.session.add(model)
            self.session.commit()

        except Exception as e:
            logging.error(f"Unexpected Error Occured: {e}")
            return {"error": "Unexpected Error Occured"}

        return {"success": "Model Details stored successfully"}

    def fetchModels(self) -> List[Dict[str, Union[str, int]]]:
        try:
            models = self.session.query(Models.id, Models.model_name, Models.description, ModelsConfig.source_name).join(ModelsConfig, Models.model_provider_id == ModelsConfig.id).filter(Models.org_id == self.organisation_id).all()

            result = []
            for model in models:
                result.append({
                    "id": model[0],
                    "name": model[1],
                    "description": model[2],
                    "model_provider": model[3]
                })

        except Exception as e:
            logging.error(f"Unexpected Error Occured: {e}")
            return {"error": "Unexpected Error Occured"}

        return result

    def fetchModelDetails(self, model_id: int) -> Dict[str, Union[str, int]]:
        try:
            model = self.session.query(
                Models.id, Models.model_name, Models.description,
                Models.end_point, Models.token_limit, ModelsConfig.source_name
            ).join(
                ModelsConfig, Models.model_provider_id == ModelsConfig.id
            ).filter(
                and_(Models.org_id == self.organisation_id, Models.id == model_id)
            ).first()

            if model:
                return {
                    "id": model[0],
                    "name": model[1],
                    "description": model[2],
                    "end_point": model[3],
                    "token_limit": model[4],
                    "model_provider": model[5]
                }
            else:
                return {"error": "Model with the given ID doesn't exist."}

        except Exception as e:
            logging.error(f"Unexpected Error Occured: {e}")
            return {"error": "Unexpected Error Occured"}