from enum import Enum

class ToolConfigKeyType(Enum):
    STRING = 'string'
    FILE = 'file'
    INT = 'int'

    @classmethod
    def get_key_type(cls, store):
        if store is None:
            raise ValueError("Key type cannot be None.")
        store = str(store).upper().strip()
        if store in cls.__members__:
            return cls[store]
        raise ValueError(f"{store} is not a valid key type.")

    def __str__(self):
        return self.value
