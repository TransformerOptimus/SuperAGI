import json

from sqlalchemy import asc

from superagi.agent.agent_message_builder import AgentLlmMessageBuilder
from superagi.agent.output_handler import ToolOutputHandler
from superagi.agent.tool_builder import ToolBuilder
from superagi.helper.prompt_reader import PromptReader
from superagi.helper.token_counter import TokenCounter
from superagi.models.agent import Agent
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_execution_config import AgentExecutionConfiguration
from superagi.models.agent_execution_feed import AgentExecutionFeed
from superagi.models.workflows.agent_workflow_step import AgentWorkflowStep
from superagi.models.workflows.agent_workflow_step_tool import AgentWorkflowStepTool
from superagi.models.workflows.iteration_workflow import IterationWorkflow
from superagi.resource_manager.resource_summary import ResourceSummarizer
from superagi.tools.base_tool import BaseTool


class AgentToolStepHandler:
    def __init__(self, session, llm, agent_id: int, agent_execution_id: int, memory = None):
        self.session = session
        self.llm = llm
        self.agent_execution_id = agent_execution_id
        self.agent_id = agent_id
        self.memory = memory

    def execute_step(self):
        execution = AgentExecution.get_agent_execution_from_id(self.session, self.agent_execution_id)
        workflow_step = AgentWorkflowStep.find_by_id(self.session, execution.current_step_id)
        step_tool = AgentWorkflowStepTool.find_by_id(self.session, workflow_step.action_reference_id)
        agent_config = Agent.fetch_configuration(self.session, self.agent_id)
        agent_execution_config = AgentExecutionConfiguration.fetch_configuration(self.session, self.agent_execution_id)

        assistant_reply = self._process_input_instruction(agent_config, agent_execution_config, step_tool,
                                                          workflow_step)
        tool_obj = self._build_tool_obj(agent_config, agent_execution_config, step_tool.tool_name)
        final_response = ToolOutputHandler(self.agent_execution_id, agent_config, [tool_obj]).handle(self.session, assistant_reply)
        step_response = "default"
        if step_tool.output_instruction:
            step_response = self._process_output_instruction(final_response, step_tool, workflow_step)

        next_step = AgentWorkflowStep.fetch_next_step(self.session, workflow_step.id, step_response)
        agent_execution = AgentExecution.get_agent_execution_from_id(self.session, self.agent_execution_id)
        if str(next_step) == "COMPLETE":
            agent_execution.current_step_id = -1
            agent_execution.status = "COMPLETED"
            self.session.commit()
        else:
            agent_execution.current_step_id = next_step.id
            if next_step.action_type == "ITERATION_WORKFLOW":
                trigger_step = IterationWorkflow.fetch_trigger_step_id(self.session, next_step.action_reference_id)
                agent_execution.iteration_workflow_step_id = trigger_step.id

            self.session.commit()
        self.session.flush()

    def _process_input_instruction(self, agent_config, agent_execution_config, step_tool, workflow_step):
        tool_obj = self._build_tool_obj(agent_config, agent_execution_config, step_tool.tool_name)
        prompt = self._build_tool_input_prompt(step_tool, tool_obj, agent_execution_config)
        agent_feeds = self._fetch_agent_feeds()
        messages = AgentLlmMessageBuilder(self.session, self.llm.get_model(), self.agent_id, self.agent_execution_id) \
            .build_agent_messages(prompt, agent_feeds, history_enabled=workflow_step.history_enabled,
                                  completion_prompt=workflow_step.completion_prompt)
        current_tokens = TokenCounter.count_message_tokens(messages, self.llm.get_model())
        response = self.llm.chat_completion(messages, TokenCounter.token_limit(self.llm.get_model()) - current_tokens)
        if 'content' not in response or response['content'] is None:
            raise RuntimeError(f"Failed to get response from llm")
        total_tokens = current_tokens + TokenCounter.count_message_tokens(response, self.llm.get_model())
        AgentExecution.update_tokens(self.session, self.agent_execution_id, total_tokens)
        assistant_reply = response['content']
        return assistant_reply

    def _build_tool_obj(self, agent_config, agent_execution_config, tool_name: str):
        model_api_key = AgentConfiguration.get_model_api_key(self.session, self.agent_id, agent_config["model"])
        tool_builder = ToolBuilder(self.session, self.agent_id, self.agent_execution_id)
        resource_summary = ""
        if tool_name == "QueryResourceTool":
            resource_summary = ResourceSummarizer(session=self.session,
                                                  agent_id=self.agent_id).fetch_or_create_agent_resource_summary(
                default_summary=agent_config.get("resource_summary"))
        tool_obj = tool_builder.build_tool(tool_name)
        tool_obj = tool_builder.set_default_params_tool(tool_obj, agent_config, agent_execution_config, self.agent_id,
                                                        model_api_key, resource_summary)
        return tool_obj

    def _process_output_instruction(self, final_response: str, step_tool: AgentWorkflowStepTool,
                                    workflow_step: AgentWorkflowStep):
        prompt = self._build_tool_output_prompt(step_tool, final_response, workflow_step)
        messages = [{"role": "system", "content": prompt}]
        current_tokens = TokenCounter.count_message_tokens(messages, self.llm.get_model())
        response = self.llm.chat_completion(messages,
                                            TokenCounter.token_limit(self.llm.get_model()) - current_tokens)
        if 'content' not in response or response['content'] is None:
            raise RuntimeError(f"ToolWorkflowStepHandler: Failed to get output response from llm")
        total_tokens = current_tokens + TokenCounter.count_message_tokens(response, self.llm.get_model())
        AgentExecution.update_tokens(self.session, self.agent_execution_id, total_tokens)
        step_response = response['content']
        return step_response

    def _build_tool_input_prompt(self, step_tool: AgentWorkflowStepTool, tool: BaseTool, agent_execution_config: dict):
        super_agi_prompt = PromptReader.read_agent_prompt(__file__, "agent_tool_input.txt")
        super_agi_prompt = super_agi_prompt.replace("{goals}", agent_execution_config["goals"])
        super_agi_prompt = super_agi_prompt.replace("{tool_name}", step_tool.tool_name)
        super_agi_prompt = super_agi_prompt.replace("{instruction}", step_tool.input_instruction)

        tool_schema = f"\"{tool.name}\": {tool.description}, args json schema: {json.dumps(tool.args)}"
        super_agi_prompt = super_agi_prompt.replace("{tool_schema}", tool_schema)
        return super_agi_prompt

    def _get_step_responses(self, workflow_step: AgentWorkflowStep):
        return [step["step_response"] for step in workflow_step.next_steps]

    def _build_tool_output_prompt(self, step_tool: AgentWorkflowStepTool, tool_output: str,
                                  workflow_step: AgentWorkflowStep):
        super_agi_prompt = PromptReader.read_agent_prompt(__file__, "agent_tool_input.txt")
        super_agi_prompt = super_agi_prompt.replace("{tool_output}", tool_output)
        super_agi_prompt = super_agi_prompt.replace("{tool_name}", step_tool.tool_name)
        super_agi_prompt = super_agi_prompt.replace("{instruction}", step_tool.output_instruction)

        step_responses = self._get_step_responses(workflow_step)
        step_responses.remove("default")
        super_agi_prompt = super_agi_prompt.replace("{output_options}", step_responses)
        return super_agi_prompt

    def _fetch_agent_feeds(self):
        agent_feeds = self.session.query(AgentExecutionFeed.role, AgentExecutionFeed.feed) \
            .filter(AgentExecutionFeed.agent_execution_id == self.agent_execution_id) \
            .order_by(asc(AgentExecutionFeed.created_at)) \
            .all()
        return agent_feeds[2:]
