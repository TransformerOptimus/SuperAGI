from enum import Enum


class ModelSourceType(Enum):
    GooglePalm = 'Google Palm'
    OpenAI = 'OpenAi'
    Replicate = 'Replicate'

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
        if model_name in open_ai_models:
            return ModelSourceType.OpenAI
        if model_name in google_models:
            return ModelSourceType.GooglePalm
        return ModelSourceType.OpenAI

    def __str__(self):
        return self.value