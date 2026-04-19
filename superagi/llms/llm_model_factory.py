from superagi.llms.google_palm import GooglePalm
from superagi.llms.local_llm import LocalLLM
from superagi.llms.openai import OpenAi
from superagi.llms.replicate import Replicate
from superagi.llms.hugging_face import HuggingFace
from superagi.models.models_config import ModelsConfig
from superagi.models.models import Models
from sqlalchemy.orm import sessionmaker
from superagi.models.db import connect_db
from superagi.lib.logger import logger


def get_model(organisation_id, api_key, model="gpt-3.5-turbo", **kwargs):
    logger.info("Fetching model details from database")
    engine = connect_db()
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        model_instance = session.query(Models).filter(Models.org_id == organisation_id, Models.model_name == model).first()
        if model_instance is None:
            logger.warning(f"Model '{model}' not found for organisation {organisation_id}. Falling back to OpenAI.")
            return OpenAi(api_key=api_key, model=model, **kwargs)

        response = session.query(ModelsConfig.provider).filter(ModelsConfig.org_id == organisation_id,
                                                               ModelsConfig.id == model_instance.model_provider_id).first()
        if response is None or response.provider is None:
            logger.warning(f"Provider config missing for model '{model_instance.model_name}'. Falling back to OpenAI.")
            return OpenAi(model=model_instance.model_name, api_key=api_key, **kwargs)

        provider_name = response.provider
    finally:
        session.close()

    if provider_name == 'OpenAI':
        logger.info("Provider is OpenAI")
        return OpenAi(model=model_instance.model_name, api_key=api_key, **kwargs)
    elif provider_name == 'Replicate':
        logger.info("Provider is Replicate")
        return Replicate(model=model_instance.model_name, version=model_instance.version, api_key=api_key, **kwargs)
    elif provider_name == 'Google Palm':
        logger.info("Provider is Google Palm")
        return GooglePalm(model=model_instance.model_name, api_key=api_key, **kwargs)
    elif provider_name == 'Hugging Face':
        logger.info("Provider is Hugging Face")
        return HuggingFace(model=model_instance.model_name, end_point=model_instance.end_point, api_key=api_key, **kwargs)
    elif provider_name == 'Local LLM':
        logger.info("Provider is Local LLM")
        return LocalLLM(model=model_instance.model_name, context_length=model_instance.context_length)
    else:
        logger.warning(f"Unknown provider '{provider_name}'. Falling back to OpenAI")
        return OpenAi(model=model_instance.model_name, api_key=api_key, **kwargs)

def build_model_with_api_key(provider_name, api_key):
    if provider_name.lower() == 'openai':
        return OpenAi(api_key=api_key)
    elif provider_name.lower() == 'replicate':
        return Replicate(api_key=api_key)
    elif provider_name.lower() == 'google palm':
        return GooglePalm(api_key=api_key)
    elif provider_name.lower() == 'hugging face':
        return HuggingFace(api_key=api_key)
    elif provider_name.lower() == 'local llm':
        return LocalLLM(api_key=api_key)
    else:
        logger.warning(f"Unknown provider '{provider_name}'")
        return None