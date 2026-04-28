from enum import Enum

class ModelsTypes(Enum):
    MARKETPLACE = "Marketplace"
    CUSTOM = "Custom"

    @classmethod
    def get_models_types(cls, model_type):
        if model_type is None:
            raise ValueError("Model type cannot be None.")
        model_type = str(model_type).upper().strip()
        if model_type in cls.__members__:
            return cls[model_type]
        raise ValueError(f"{model_type} is not a valid model type name.")
