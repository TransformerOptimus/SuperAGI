from enum import Enum


class AgentWorkflowStepWaitStatus(Enum):
    PENDING = 'PENDING'
    WAITING = 'WAITING'
    COMPLETED = 'COMPLETED'

    @classmethod
    def get_agent_workflow_step_wait_status(cls, store):
        if store is None:
            raise ValueError("Wait step status cannot be None.")
        store = str(store).upper().strip()
        if store in cls.__members__:
            return cls[store]
        raise ValueError(f"{store} is not a valid wait step status name.")
