from typing import List, Dict, Union, Any
from sqlalchemy import text, func, and_
from sqlalchemy.orm import Session
from superagi.models.models_config import ModelsConfig
from superagi.llms.hugging_face import HuggingFace
import requests

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
            raise Exception("No API key found for the provided model provider")

        api_keys = [{"source_name": source_name, "api_key": api_key} for source_name, api_key in api_key_info]

        return api_keys


    def fetchApiKey(self, model_provider):
        api_key_data = self.session.query(ModelsConfig.id, ModelsConfig.source_name, ModelsConfig.api_key).filter(and_(ModelsConfig.org_id == self.organisation_id, ModelsConfig.source_name == model_provider)).first()

        if api_key_data is None:
            return []
        else:
            api_key = [{'id': api_key_data.id,'source_name': api_key_data.source_name,'api_key': api_key_data.api_key}]
            return api_key


    def validateEndPoint(self, model_api_key, end_point):
        result = HuggingFace(api_key=model_api_key,end_point=end_point).get_model()
        if 'error' in result:
            return result['error']

        return result