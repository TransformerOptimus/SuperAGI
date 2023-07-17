from enum import Enum


class StorageType(Enum):
    FILE = 'FILE'
    S3 = 'S3'

    @classmethod
    def get_storage_type(cls, store):
        if store is None:
            raise ValueError("Storage type cannot be None.")
        store = store.upper()
        if store in cls.__members__:
            return cls[store]
        raise ValueError(f"{store} is not a valid storage name.")
