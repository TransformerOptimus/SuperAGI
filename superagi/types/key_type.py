from enum import Enum

class ToolConfigKeyType(Enum):
    STRING = 'string'
    FILE = 'file'
    INT = 'int'

    @classmethod
    def get_key_type(cls, store):
        store = store.upper()
        if store in cls.__members__:
            return cls[store]
        raise ValueError(f"{store} is not a valid key type.")

    def __str__(self):
        return self.value
