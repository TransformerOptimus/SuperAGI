from enum import Enum


class QueueStatus(Enum):
    INITIATED = 'INITIATED'
    PROCESSING = 'PROCESSING'
    COMPLETE = 'COMPLETE'

    @classmethod
    def get_queue_type(cls, store):
        if store is None:
            raise ValueError("Queue status type cannot be None.")
        store = store.upper()
        if store in cls.__members__:
            return cls[store]
        raise ValueError(f"{store} is not a valid storage name.")
