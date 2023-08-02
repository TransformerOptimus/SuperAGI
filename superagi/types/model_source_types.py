from enum import Enum
from superagi.llms.utils.huggingface_endpoints import HuggingFaceEndpoints

class ModelSourceType(Enum):
    GooglePalm = 'Google Palm'
    OpenAI = 'OpenAi'
    HuggingFace = 'HuggingFace'

    @classmethod
    def get_model_source_type(cls, name):
        name = name.upper().replace(" ", "")
        for member in cls.__members__:
            if name == member.upper():
                return cls[member]
        raise ValueError(f"{name} is not a valid vector store name.")

    @classmethod
    def get_model_source_from_model(cls, model_name: str):
        open_ai_models = ['gpt-4', 'gpt-3.5-turbo', 'gpt-3.5-turbo-16k', 'gpt-4-32k']
        google_models = ['google-palm-bison-001', 'models/chat-bison-001']
        huggingface_models = [model.name for model in HuggingFaceEndpoints]
        if model_name in open_ai_models:
            return ModelSourceType.OpenAI
        if model_name in google_models:
            return ModelSourceType.GooglePalm
        if model_name in huggingface_models:
            return ModelSourceType.HuggingFace
        return ModelSourceType.OpenAI

    def __str__(self):
        return self.value
