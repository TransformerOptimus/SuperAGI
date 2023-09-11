from enum import Enum


class AgentWorkflowStepWaitStatus(Enum):
    PENDING = 'PENDING'
    WAITING = 'WAITING'
    COMPLETED = 'COMPLETED'

    @classmethod
    def get_agent_workflow_step_wait_status(cls, store):
        if store is None:
            raise ValueError("Storage type cannot be None.")
        store = store.upper()
        if store in cls.__members__:
            return cls[store]
        raise ValueError(f"{store} is not a valid storage name.")
