from typing import List, Dict, Union, Any

from sqlalchemy import text, func, and_
from sqlalchemy.orm import Session
import requests

class ModelsHelper:

    def __init__(self, session:Session, organisation_id: int):
        self.session = session
        self.organisation_id = organisation_id

    def fetchModels(self):
        response = requests.get('https://huggingface.co/api/models')
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('API request unsuccessful. Status code: ', response.status_code)
