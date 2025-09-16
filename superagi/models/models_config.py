from sqlalchemy import Column, Integer, String, and_, distinct
from superagi.lib.logger import logger
from superagi.models.base_model import DBBaseModel
from superagi.models.organisation import Organisation
from superagi.models.project import Project
from superagi.models.models import Models
from superagi.llms.openai import OpenAi
from superagi.helper.encyption_helper import encrypt_data, decrypt_data
from fastapi import HTTPException
import logging

class ModelsConfig(DBBaseModel):
    """
    Represents a Model Config record in the database.

    Attributes:
        id (Integer): The unique identifier of the event.
        provider (String): The name of the model provider.
        api_key (String): The api_key for individual model providers for every Organisation
        org_id (Integer): The ID of the organisation.
    """

    __tablename__ = 'models_config'

    id = Column(Integer, primary_key=True)
    provider = Column(String, nullable=False)
    api_key = Column(String, nullable=False)
    org_id = Column(Integer, nullable=False)

    def __repr__(self):
        """
        Returns a string representation of the ModelsConfig instance.
        """
        return f"ModelsConfig(id={self.id}, provider={self.provider}, " \
               f"org_id={self.org_id})"

    @classmethod
    def fetch_value_by_agent_id(cls, session, agent_id: int, model: str):
        """
        Fetches the configuration of an agent.

        Args:
            session: The database session object.
            agent_id (int): The ID of the agent.
            model (str): The model of the configuration.

        Returns:
            dict: Parsed configuration.

        """
        from superagi.models.agent import Agent
        agent = session.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        project = session.query(Project).filter(Project.id == agent.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        organisation = session.query(Organisation).filter(Organisation.id == project.organisation_id).first()
        if not organisation:
            raise HTTPException(status_code=404, detail="Organisation not found")

        model_provider = session.query(Models).filter(Models.org_id == organisation.id, Models.model_name == model).first()
        if not model_provider:
            raise HTTPException(status_code=404, detail="Model provider not found")

        config = session.query(ModelsConfig.provider, ModelsConfig.api_key).filter(ModelsConfig.org_id == organisation.id, ModelsConfig.id == model_provider.model_provider_id).first()

        if not config:
            return None

        if config.provider == 'Local LLM':
            return {"provider": config.provider, "api_key": config.api_key} if config else None

        return {"provider": config.provider, "api_key": decrypt_data(config.api_key)} if config else None

    @classmethod
    def store_api_key(cls, session, organisation_id, model_provider, model_api_key):
        existing_entry = session.query(ModelsConfig).filter(and_(ModelsConfig.org_id == organisation_id,
                                                                 ModelsConfig.provider == model_provider)).first()
        if existing_entry:
            existing_entry.api_key = encrypt_data(model_api_key)
            session.commit()
            session.flush()
            if model_provider == 'OpenAI':
                cls.storeGptModels(session, organisation_id, existing_entry.id, model_api_key)
            result = {'message': 'The API key was successfully updated'}
        else:
            new_entry = ModelsConfig(org_id=organisation_id, provider=model_provider,
                                     api_key=encrypt_data(model_api_key))
            session.add(new_entry)
            session.commit()
            session.flush()
            if model_provider == 'OpenAI':
                cls.storeGptModels(session, organisation_id, new_entry.id, model_api_key)
            result = {'message': 'The API key was successfully stored', 'model_provider_id': new_entry.id}

        return result

    @classmethod
    def storeGptModels(cls, session, organisation_id, model_provider_id, model_api_key):
        # Updated default models with latest GPT models and their token limits as of 2024
        default_models = {
            # GPT-3.5 models - corrected token limits
            "gpt-3.5-turbo": 16385,  # Updated from 4096 to current limit
            "gpt-3.5-turbo-0125": 16385,
            "gpt-3.5-turbo-1106": 16385,
            "gpt-3.5-turbo-instruct": 4097,  # Updated limit
            # Legacy GPT-3.5 models (for backward compatibility)
            "gpt-3.5-turbo-16k": 16384,  # Legacy model ID
            # GPT-4 models - updated token limits
            "gpt-4": 8192, 
            "gpt-4-32k": 32768,  # Legacy model, may not be available
            "gpt-4-0125-preview": 128000,
            "gpt-4-1106-preview": 128000,
            "gpt-4-turbo": 128000,
            "gpt-4-turbo-2024-04-09": 128000,  # Latest turbo version
            "gpt-4-turbo-preview": 128000,
            # Latest GPT-4o models
            "gpt-4o": 128000,
            "gpt-4o-2024-08-06": 128000,  # Latest version
            "gpt-4o-mini": 128000,
            "gpt-4o-mini-2024-07-18": 128000,  # Latest mini version
            # New reasoning models
            "o1-preview": 128000,  # New reasoning model
            "o1-mini": 128000  # New reasoning model (mini version)
        }
        models = OpenAi(api_key=model_api_key).get_models()
        installed_models = [model[0] for model in session.query(Models.model_name).filter(Models.org_id == organisation_id).all()]
        for model in models:
            if model not in installed_models and model in default_models:
                result = Models.store_model_details(session, organisation_id, model, model, '',
                                                 model_provider_id, default_models[model], 'Custom', '', 0)

    @classmethod
    def fetch_api_keys(cls, session, organisation_id):
        api_key_info = session.query(ModelsConfig.provider, ModelsConfig.api_key).filter(
            ModelsConfig.org_id == organisation_id).all()

        if not api_key_info:
            logging.error("No API key found for the provided model provider")
            return []

        api_keys = [{"provider": provider, "api_key": decrypt_data(api_key)} for provider, api_key in api_key_info if api_key != 'EMPTY']

        return api_keys

    @classmethod
    def fetch_api_key(cls, session, organisation_id, model_provider):
        api_key_data = session.query(ModelsConfig.id, ModelsConfig.provider, ModelsConfig.api_key).filter(
            and_(ModelsConfig.org_id == organisation_id, ModelsConfig.provider == model_provider)).first()

        logger.info(api_key_data)
        if api_key_data is None:
            return []
        elif api_key_data.provider == 'Local LLM':
            api_key = [{'id': api_key_data.id, 'provider': api_key_data.provider,
                        'api_key': api_key_data.api_key}]
            return api_key
        else:
            api_key = [{'id': api_key_data.id, 'provider': api_key_data.provider,
                        'api_key': decrypt_data(api_key_data.api_key)}]
            return api_key

    @classmethod
    def fetch_model_by_id(cls, session, organisation_id, model_provider_id):
        model = session.query(ModelsConfig.provider).filter(ModelsConfig.id == model_provider_id,
                                                            ModelsConfig.org_id == organisation_id).first()
        if model is None:
            return {"error": "Model not found"}
        else:
            return {"provider": model.provider}

    @classmethod
    def fetch_model_by_id_marketplace(cls, session, model_provider_id):
        model = session.query(ModelsConfig.provider).filter(ModelsConfig.id == model_provider_id).first()
        if model is None:
            return {"error": "Model not found"}
        else:
            return {"provider": model.provider}
    
    @classmethod
    def add_llm_config(cls, session, organisation_id):
        existing_models_config = session.query(ModelsConfig).filter(ModelsConfig.org_id == organisation_id, ModelsConfig.provider == 'Local LLM').first()
        if existing_models_config is None:
            models_config = ModelsConfig(org_id=organisation_id, provider='Local LLM', api_key="EMPTY")
            session.add(models_config)
            session.commit()