from enum import Enum


class AgentWorkflowStepAction(Enum):
    ITERATION_WORKFLOW = 'ITERATION_WORKFLOW'
    TOOL = 'TOOL'
    WAIT_STEP = 'WAIT_STEP'


    @classmethod
    def get_agent_workflow_action_type(cls, store):
        if store is None:
            raise ValueError("Storage type cannot be None.")
        store = store.upper()
        if store in cls.__members__:
            return cls[store]
        raise ValueError(f"{store} is not a valid storage name.")
