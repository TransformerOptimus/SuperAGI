from superagi.llms.google_palm import GooglePalm
from superagi.llms.openai import OpenAi
from superagi.llms.replicate import Replicate
from superagi.llms.hugging_face import HuggingFace
from superagi.models.models_config import ModelsConfig
from superagi.models.models import Models
from sqlalchemy.orm import sessionmaker
from superagi.models.db import connect_db

class ModelFactory:
    def __init__(self):
        self._creators = {}

    def register_format(self, model, creator):
        self._creators[model] = creator

    def get_model(self, model, **kwargs):
        creator = self._creators.get(model)
        if not creator:
            raise ValueError(model)
        return creator(**kwargs)


factory = ModelFactory()

def get_model(organisation_id, api_key, model="gpt-3.5-turbo", **kwargs):
    print("Fetching model details from database...")
    engine = connect_db()
    Session = sessionmaker(bind=engine)
    session = Session()

    model_instance = session.query(Models).filter(Models.org_id == organisation_id, Models.model_name == model).first()
    response = session.query(ModelsConfig.source_name).filter(ModelsConfig.org_id == organisation_id,
                                                                   ModelsConfig.id == model_instance.model_provider_id).first()
    provider_name = response.source_name

    session.close()

    if provider_name == 'OpenAI':
        print("Provider is OpenAI")
        factory.register_format(model_instance.model_name, lambda **kwargs: OpenAi(model=model_instance.model_name, **kwargs))
    elif provider_name == 'Replicate':
        print("Provider is Replicate")
        factory.register_format(model_instance.model_name, lambda **kwargs: Replicate(model=model_instance.model_name,
                                                       version=model_instance.version,
                                                       **kwargs))
    elif provider_name == 'Google Palm':
        print("Provider is Google Palm")
        factory.register_format(model_instance.model_name, lambda **kwargs: GooglePalm(model=model_instance.model_name, **kwargs))
    elif provider_name == 'Hugging Face':
        print("Provider is Hugging Face")
        factory.register_format(model_instance.model_name, lambda **kwargs: HuggingFace(model=model_instance.model_name,
                                                                                        end_point=model_instance.endpoint, **kwargs))
    return factory.get_model(model, api_key=api_key, **kwargs)
