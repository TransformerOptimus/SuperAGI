from typing import List, Dict, Union, Any
from sqlalchemy import text, func, and_
from sqlalchemy.orm import Session
from superagi.models.models_config import ModelsConfig
import requests

class ModelsHelper:

    def __init__(self, session:Session, organisation_id: int):
        self.session = session
        self.organisation_id = organisation_id

    def storeApiKey(self, model_provider, model_api_key):
        # check if the model_provider already exists
        existing_entry = self.session.query(ModelsConfig).filter(and_(ModelsConfig.organisation_id == self.organisation_id, ModelsConfig.model_provider == model_provider)).first()

        # if it already exists, update the key
        if existing_entry:
            existing_entry.model_api_key = model_api_key
        else:
            # if it doesn't exist, create a new entry
            new_entry = ModelsConfig(organisation_id=self.organisation_id, model_provider=model_provider, model_api_key=model_api_key)
            self.session.add(new_entry)

        # commit the changes
        self.session.commit()

        return {'message': 'The API key was successfully stored'}
