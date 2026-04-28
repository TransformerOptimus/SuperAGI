from enum import Enum


class AgentExecutionStatus(Enum):
    RUNNING = 'RUNNING'
    WAITING_FOR_PERMISSION = 'WAITING_FOR_PERMISSION'
    ITERATION_LIMIT_EXCEEDED = 'ITERATION_LIMIT_EXCEEDED'
    WAIT_STEP = 'WAIT_STEP'
    COMPLETED = 'COMPLETED'

    @classmethod
    def get_agent_execution_status(cls, store):
        if store is None:
            raise ValueError("Agent execution status cannot be None.")
        store = str(store).upper().strip()
        if store in cls.__members__:
            return cls[store]
        raise ValueError(f"{store} is not a valid agent execution status name.")
