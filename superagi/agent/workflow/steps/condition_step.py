from superagi.agent.agent_prompt_builder import AgentPromptBuilder
from superagi.agent.types.agent_execution_status import AgentExecutionStatus
from superagi.agent.types.agent_workflow_step_action_types import AgentWorkflowStepAction
from superagi.helper.prompt_reader import PromptReader
from superagi.helper.token_counter import TokenCounter
from superagi.lib.logger import logger
from superagi.models.agent import Agent
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_execution_config import AgentExecutionConfiguration
from superagi.models.workflows.agent_workflow_step import AgentWorkflowStep
from superagi.models.workflows.agent_workflow_step_condition import AgentWorkflowStepCondition


class AgentConditionStepHandler:
    """Handle Agent Wait Step in the agent workflow."""

    def __init__(self, session, agent_id, agent_execution_id, llm):
        self.session = session
        self.agent_id = agent_id
        self.agent_execution_id = agent_execution_id
        self.llm = llm
        self.organisation = Agent.find_org_by_agent_id(self.session, self.agent_id)

    def execute_step(self):
        """Execute the agent condition step."""

        logger.info("Executing Condition Step")
        execution = AgentExecution.get_agent_execution_from_id(self.session, self.agent_execution_id)
        agent_execution_config = AgentExecutionConfiguration.fetch_configuration(self.session, self.agent_execution_id)
        workflow_step = AgentWorkflowStep.find_by_id(self.session, execution.current_agent_step_id)
        step_condition = AgentWorkflowStepCondition.find_by_id(self.session, workflow_step.action_reference_id)
        step_condition_prompt = self._build_condition_prompt(step_condition, workflow_step,agent_execution_config)
        messages = [{"role": "system", "content": step_condition_prompt}]
        current_tokens = TokenCounter.count_message_tokens(messages, self.llm.get_model())
        response = self.llm.chat_completion(messages,
                                            TokenCounter(session=self.session,
                                                         organisation_id=self.organisation.id).token_limit(
                                                self.llm.get_model()) - current_tokens)
        if 'content' not in response or response['content'] is None:
            raise RuntimeError(f"ToolWorkflowStepHandler: Failed to get output response from llm")
        total_tokens = current_tokens + TokenCounter.count_message_tokens(response, self.llm.get_model())
        AgentExecution.update_tokens(self.session, self.agent_execution_id, total_tokens)
        step_response = response['content']
        step_response = step_response.replace("'", "").replace("\"", "")
        print("CONDITIONAL RESPONSE: ", step_response)
        next_step = AgentWorkflowStep.fetch_next_step(self.session, workflow_step.id, step_response)
        self._handle_next_step(next_step)

    def update_tool_output(self, tool_output, tool_name, next_step):
        if next_step.action_type == AgentWorkflowStepAction.CONDITION.value:
            # update the tool output in the condition step
            AgentWorkflowStepCondition.update_tool_info(self.session, next_step.unique_id,
                                                        tool_output, tool_name)

    def _build_condition_prompt(self, step_condition, workflow_step,agent_execution_config):
        # super_agi_prompt = PromptReader.read_agent_prompt(__file__, "agent_tool_output.txt")
        super_agi_prompt = """Analyze {tool_name} output and follow the instruction to come up with the response:
High-Level GOAL:
`{goals}`

TOOL OUTPUT:
`{tool_output}`

INSTRUCTION: `{instruction}`

Analyze the instruction and respond with one of the below outputs. Response should be one of the below options:
{output_options}"""
        super_agi_prompt = super_agi_prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(
            agent_execution_config["goal"]))
        super_agi_prompt = super_agi_prompt.replace("{tool_output}", step_condition.tool_output)
        super_agi_prompt = super_agi_prompt.replace("{tool_name}", step_condition.tool_name)
        super_agi_prompt = super_agi_prompt.replace("{instruction}", step_condition.instruction)

        step_responses = self._get_step_responses(workflow_step)
        if "default" in step_responses:
            step_responses.remove("default")
        super_agi_prompt = super_agi_prompt.replace("{output_options}", str(step_responses))
        return super_agi_prompt

    def _get_step_responses(self, workflow_step: AgentWorkflowStep):
        return [step["step_response"] for step in workflow_step.next_steps]

    # TODO: This method can be brought to an abstract method and can be used in all the steps
    # TODO: interface can have a execute_step which needs to be implemented differently for each step
    # TODO: common attributes can be moved to the abstract class

    def _handle_next_step(self, next_step):
        if str(next_step) == "COMPLETE":
            agent_execution = AgentExecution.get_agent_execution_from_id(self.session, self.agent_execution_id)
            agent_execution.current_agent_step_id = -1
            agent_execution.status = AgentExecutionStatus.COMPLETED.value
        else:
            AgentExecution.assign_next_step_id(self.session, self.agent_execution_id, next_step.id)
        self.session.commit()
