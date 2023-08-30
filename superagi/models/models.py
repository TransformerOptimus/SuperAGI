from sqlalchemy import Column, Integer, String, and_
from sqlalchemy.sql import func
from typing import List, Dict, Union
from superagi.models.base_model import DBBaseModel
from superagi.llms.openai import OpenAi
from superagi.helper.encyption_helper import decrypt_data
import requests, logging

# marketplace_url = "https://app.superagi.com/api"
marketplace_url = "http://localhost:8001"
class Models(DBBaseModel):
    """
    Represents a Model record in the database

    Attributes:
        id (Integer): The unique identifier of the event.
        model_name (String): The name of the model.
        description (String): The description for the model.
        end_point (String): The end_point for the model.3001
        model_provider_id (Integer): The unique id of the model_provider from the models_config table.
        token_limit (Integer): The maximum number of tokens for a model.
        type (Strng): The place it is added from.
        version (String): The version of the replicate model.
        org_id (Integer): The ID of the organisation.
        model_features (String): The Features of the Model.
    """

    __tablename__ = 'models'

    id = Column(Integer, primary_key=True)
    model_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    end_point = Column(String, nullable=False)
    model_provider_id = Column(Integer, nullable=False)
    token_limit = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    version = Column(String, nullable=False)
    org_id = Column(Integer, nullable=False)
    model_features = Column(String, nullable=False)

    def __repr__(self):
        """
        Returns a string representation of the Models instance.
        """
        return f"Models(id={self.id}, model_name={self.model_name}, " \
               f"end_point={self.end_point}, model_provider_id={self.model_provider_id}, " \
               f"token_limit={self.token_limit}, " \
               f"type={self.type}, " \
               f"version={self.version}, " \
               f"org_id={self.org_id}, " \
               f"model_features={self.model_features})"

    @classmethod
    def fetch_marketplace_list(cls, page):
        headers = {'Content-Type': 'application/json'}
        response = requests.get(
            marketplace_url + f"/models_controller/marketplace/list/{str(page)}",
            headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return []

    @classmethod
    def get_model_install_details(cls, session, marketplace_models, organisation):
        from superagi.models.models_config import ModelsConfig
        installed_models = session.query(Models).filter(Models.org_id == organisation.id).all()
        model_counts_dict = dict(
            session.query(Models.model_name, func.count(Models.org_id)).group_by(Models.model_name).all()
        )
        installed_models_dict = {model.model_name: True for model in installed_models}

        for model in marketplace_models:
            try:
                model["is_installed"] = installed_models_dict.get(model["model_name"], False)
                model["installs"] = model_counts_dict.get(model["model_name"], 0)
                model["provider"] = session.query(ModelsConfig).filter(
                    ModelsConfig.id == model["model_provider_id"]).first().provider
            except TypeError as e:
                logging.error("Error Occurred: %s", e)

        return marketplace_models

    @classmethod
    def fetch_model_tokens(cls, session, organisation_id) -> Dict[str, int]:
        try:
            models = session.query(
                Models.model_name, Models.token_limit
            ).filter(
                Models.org_id == organisation_id
            ).all()

            if models:
                return dict(models)
            else:
                return {"error": "No models found for the given organisation ID."}

        except Exception as e:
            logging.error(f"Unexpected Error Occured: {e}")
            return {"error": "Unexpected Error Occured"}

    @classmethod
    def store_model_details(cls, session, organisation_id, model_name, description, end_point, model_provider_id, token_limit, type, version):
        from superagi.models.models_config import ModelsConfig
        if not model_name:
            return {"error": "Model Name is empty or undefined"}
        if not description:
            return {"error": "Description is empty or undefined"}
        if not model_provider_id:
            return {"error": "Model Provider Id is null or undefined or 0"}
        if not token_limit:
            return {"error": "Token Limit is null or undefined or 0"}

        # Check if model_name already exists in the database
        existing_model = session.query(Models).filter(Models.model_name == model_name, Models.org_id == organisation_id).first()
        if existing_model:
            return {"error": "Model Name already exists"}

        # Get the provider of the model
        if type == 'Marketplace':
            model = ModelsConfig.fetch_model_by_id_marketplace(session, model_provider_id)
        else:
            model = ModelsConfig.fetch_model_by_id(session, organisation_id, model_provider_id)

        if "error" in model:
            return model  # Return error message if model not found

        # Check the 'provider' from ModelsConfig table
        if not end_point and model["provider"] not in ['OpenAI', 'Google Palm', 'Replicate']:
            return {"error": "End Point is empty or undefined"}

        try:
            model = Models(
                model_name=model_name,
                description=description,
                end_point=end_point,
                token_limit=token_limit,
                model_provider_id=model_provider_id,
                type=type,
                version=version,
                org_id=organisation_id,
                model_features=''
            )
            session.add(model)
            session.commit()
            session.flush()

        except Exception as e:
            logging.error(f"Unexpected Error Occured: {e}")
            return {"error": "Unexpected Error Occured"}

        return {"success": "Model Details stored successfully", "model_id": model.id}

    @classmethod
    def api_key_from_configurations(cls, session, organisation_id):
        try:
            from superagi.models.models_config import ModelsConfig
            from superagi.models.configuration import Configuration

            model_provider = session.query(ModelsConfig).filter(ModelsConfig.provider == "OpenAI",
                                                                ModelsConfig.org_id == organisation_id).first()
            if model_provider is None:
                configurations = session.query(Configuration).filter(Configuration.key == 'model_api_key',
                                                                     Configuration.organisation_id == organisation_id).first()

                if configurations is None:
                    return {"error": "API Key is Missing"}
                else:
                    model_api_key = decrypt_data(configurations.value)
                    model_details = ModelsConfig.store_api_key(session, organisation_id, "OpenAI", model_api_key)
        except Exception as e:
            logging.error(f"Exception has been raised while checking API Key:: {e}")


    @classmethod
    def fetch_models(cls, session, organisation_id) -> Union[Dict[str, str], List[Dict[str, Union[str, int]]]]:
        try:
            from superagi.models.models_config import ModelsConfig
            cls.api_key_from_configurations(session, organisation_id)

            models = session.query(Models.id, Models.model_name, Models.description, ModelsConfig.provider).join(
                ModelsConfig, Models.model_provider_id == ModelsConfig.id).filter(
                Models.org_id == organisation_id).all()

            result = []
            for model in models:
                result.append({
                    "id": model[0],
                    "name": model[1],
                    "description": model[2],
                    "model_provider": model[3]
                })

        except Exception as e:
            logging.error(f"Unexpected Error Occurred: {e}")
            return {"error": "Unexpected Error Occurred"}

        return result

    @classmethod
    def fetch_model_details(cls, session, organisation_id, model_id: int) -> Dict[str, Union[str, int]]:
        try:
            from superagi.models.models_config import ModelsConfig
            model = session.query(
                Models.id, Models.model_name, Models.description, Models.end_point, Models.token_limit, Models.type,
                ModelsConfig.provider,
            ).join(
                ModelsConfig, Models.model_provider_id == ModelsConfig.id
            ).filter(
                and_(Models.org_id == organisation_id, Models.id == model_id)
            ).first()

            if model:
                return {
                    "id": model[0],
                    "name": model[1],
                    "description": model[2],
                    "end_point": model[3],
                    "token_limit": model[4],
                    "type": model[5],
                    "model_provider": model[6]
                }
            else:
                return {"error": "Model with the given ID doesn't exist."}

        except Exception as e:
            logging.error(f"Unexpected Error Occured: {e}")
            return {"error": "Unexpected Error Occured"}
