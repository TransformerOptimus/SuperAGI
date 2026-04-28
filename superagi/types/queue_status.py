from enum import Enum


class QueueStatus(Enum):
    INITIATED = 'INITIATED'
    PROCESSING = 'PROCESSING'
    COMPLETE = 'COMPLETE'

    @classmethod
    def get_queue_type(cls, store):
        if store is None:
            raise ValueError("Queue status type cannot be None.")
        store = str(store).upper().strip()
        if store in cls.__members__:
            return cls[store]
        raise ValueError(f"{store} is not a valid queue status name.")
