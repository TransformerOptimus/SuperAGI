from enum import Enum


class AgentWorkflowStepAction(Enum):
    ITERATION_WORKFLOW = 'ITERATION_WORKFLOW'
    TOOL = 'TOOL'
    WAIT_STEP = 'WAIT_STEP'
    CONDITION = 'CONDITION'

    @classmethod
    def get_agent_workflow_action_type(cls, step_action):
        if step_action is None:
            raise ValueError("Storage type cannot be None.")
        step_action = step_action.upper()
        if step_action in cls.__members__:
            return cls[step_action]
        raise ValueError(f"{step_action} is not a valid storage name.")
