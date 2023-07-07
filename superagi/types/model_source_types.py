from enum import Enum


class ModelSourceType(Enum):
    GooglePalm = 'Google Palm'
    OpenAI = 'OpenAi'

    @classmethod
    def get_model_source_type(cls, store):
        store = store.upper()
        if store in cls.__members__:
            return cls[store]
        raise ValueError(f"{store} is not a valid vector store name.")

    def __str__(self):
        return self.value