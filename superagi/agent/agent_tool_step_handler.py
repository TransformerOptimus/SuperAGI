import json

from superagi.agent.agent_message_builder import AgentLlmMessageBuilder
from superagi.agent.agent_prompt_builder import AgentPromptBuilder
from superagi.agent.output_handler import ToolOutputHandler
from superagi.agent.output_parser import AgentSchemaToolOutputParser
from superagi.agent.queue_step_handler import QueueStepHandler
from superagi.agent.tool_builder import ToolBuilder
from superagi.helper.prompt_reader import PromptReader
from superagi.helper.token_counter import TokenCounter
from superagi.lib.logger import logger
from superagi.models.agent import Agent
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_execution_config import AgentExecutionConfiguration
from superagi.models.agent_execution_feed import AgentExecutionFeed
from superagi.models.agent_execution_permission import AgentExecutionPermission
from superagi.models.tool import Tool
from superagi.models.toolkit import Toolkit
from superagi.models.workflows.agent_workflow_step import AgentWorkflowStep
from superagi.models.workflows.agent_workflow_step_tool import AgentWorkflowStepTool
from superagi.resource_manager.resource_summary import ResourceSummarizer
from superagi.tools.base_tool import BaseTool
from sqlalchemy import and_

class AgentToolStepHandler:
    """Handles the tools steps in the agent workflow"""
    def __init__(self, session, llm, agent_id: int, agent_execution_id: int, memory=None):
        self.session = session
        self.llm = llm
        self.agent_execution_id = agent_execution_id
        self.agent_id = agent_id
        self.memory = memory

    def execute_step(self):
        execution = AgentExecution.get_agent_execution_from_id(self.session, self.agent_execution_id)
        workflow_step = AgentWorkflowStep.find_by_id(self.session, execution.current_agent_step_id)
        step_tool = AgentWorkflowStepTool.find_by_id(self.session, workflow_step.action_reference_id)
        agent_config = Agent.fetch_configuration(self.session, self.agent_id)
        agent_execution_config = AgentExecutionConfiguration.fetch_configuration(self.session, self.agent_execution_id)
        # print(agent_execution_config)

        if not self._handle_wait_for_permission(execution, workflow_step):
            return

        if step_tool.tool_name == "TASK_QUEUE":
            step_response = QueueStepHandler(self.session, self.llm, self.agent_id, self.agent_execution_id).execute_step()
            next_step = AgentWorkflowStep.fetch_next_step(self.session, workflow_step.id, step_response)
            self._handle_next_step(next_step)
            return

        if step_tool.tool_name == "WAIT_FOR_PERMISSION":
            self._create_permission_request(execution, step_tool)
            return

        assistant_reply = self._process_input_instruction(agent_config, agent_execution_config, step_tool,
                                                          workflow_step)
        tool_obj = self._build_tool_obj(agent_config, agent_execution_config, step_tool.tool_name)
        tool_output_handler = ToolOutputHandler(self.agent_execution_id, agent_config, [tool_obj],
                                                output_parser=AgentSchemaToolOutputParser())
        final_response = tool_output_handler.handle(self.session, assistant_reply)
        step_response = "default"
        if step_tool.output_instruction:
            step_response = self._process_output_instruction(final_response.result, step_tool, workflow_step)

        next_step = AgentWorkflowStep.fetch_next_step(self.session, workflow_step.id, step_response)
        self._handle_next_step(next_step)
        self.session.flush()

    def _create_permission_request(self, execution, step_tool: AgentWorkflowStepTool):
        new_agent_execution_permission = AgentExecutionPermission(
            agent_execution_id=self.agent_execution_id,
            status="PENDING",
            agent_id=self.agent_id,
            tool_name="WAIT_FOR_PERMISSION",
            question=step_tool.input_instruction,
            assistant_reply="")
        self.session.add(new_agent_execution_permission)
        self.session.commit()
        self.session.flush()
        execution.permission_id = new_agent_execution_permission.id
        execution.status = "WAITING_FOR_PERMISSION"
        self.session.commit()

    def _handle_next_step(self, next_step):
        if str(next_step) == "COMPLETE":
            agent_execution = AgentExecution.get_agent_execution_from_id(self.session, self.agent_execution_id)
            agent_execution.current_agent_step_id = -1
            agent_execution.status = "COMPLETED"
        else:
            AgentExecution.assign_next_step_id(self.session, self.agent_execution_id, next_step.id)
        self.session.commit()

    def _process_input_instruction(self, agent_config, agent_execution_config, step_tool, workflow_step):
        tool_obj = self._build_tool_obj(agent_config, agent_execution_config, step_tool.tool_name)
        prompt = self._build_tool_input_prompt(step_tool, tool_obj, agent_execution_config)
        logger.info("Prompt: ", prompt)
        agent_feeds = AgentExecutionFeed.fetch_agent_execution_feeds(self.session, self.agent_execution_id)
        messages = AgentLlmMessageBuilder(self.session, self.llm, self.agent_id, self.agent_execution_id) \
            .build_agent_messages(prompt, agent_feeds, history_enabled=step_tool.history_enabled,
                                  completion_prompt=step_tool.completion_prompt)
        # print(messages)
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

        organisation = Agent.find_org_by_agent_id(self.session, self.agent_id)
        tool = self.session.query(Tool).join(Toolkit, and_(Tool.toolkit_id == Toolkit.id, Toolkit.organisation_id == organisation.id, Tool.name == tool_name)).first()
        tool_obj = tool_builder.build_tool(tool)
        tool_obj = tool_builder.set_default_params_tool(tool_obj, agent_config, agent_execution_config, model_api_key,
                                                        resource_summary)
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
        step_response = step_response.replace("'", "").replace("\"", "")
        return step_response

    def _build_tool_input_prompt(self, step_tool: AgentWorkflowStepTool, tool: BaseTool, agent_execution_config: dict):
        super_agi_prompt = PromptReader.read_agent_prompt(__file__, "agent_tool_input.txt")
        super_agi_prompt = super_agi_prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(
            agent_execution_config["goal"]))
        super_agi_prompt = super_agi_prompt.replace("{tool_name}", step_tool.tool_name)
        super_agi_prompt = super_agi_prompt.replace("{instruction}", step_tool.input_instruction)

        tool_schema = f"\"{tool.name}\": {tool.description}, args json schema: {json.dumps(tool.args)}"
        super_agi_prompt = super_agi_prompt.replace("{tool_schema}", tool_schema)
        return super_agi_prompt

    def _get_step_responses(self, workflow_step: AgentWorkflowStep):
        return [step["step_response"] for step in workflow_step.next_steps]

    def _build_tool_output_prompt(self, step_tool: AgentWorkflowStepTool, tool_output: str,
                                  workflow_step: AgentWorkflowStep):
        super_agi_prompt = PromptReader.read_agent_prompt(__file__, "agent_tool_output.txt")
        super_agi_prompt = super_agi_prompt.replace("{tool_output}", tool_output)
        super_agi_prompt = super_agi_prompt.replace("{tool_name}", step_tool.tool_name)
        super_agi_prompt = super_agi_prompt.replace("{instruction}", step_tool.output_instruction)

        step_responses = self._get_step_responses(workflow_step)
        if "default" in step_responses:
            step_responses.remove("default")
        super_agi_prompt = super_agi_prompt.replace("{output_options}", str(step_responses))
        return super_agi_prompt

    def _handle_wait_for_permission(self, agent_execution, workflow_step: AgentWorkflowStep):
        """
        Handles the wait for permission when the agent execution is waiting for permission.

        Args:
            agent_execution (AgentExecution): The agent execution.
            workflow_step (AgentWorkflowStep): The workflow step.

        Raises:
            Returns permission success or failure
        """
        if agent_execution.status != "WAITING_FOR_PERMISSION":
            return True
        agent_execution_permission = self.session.query(AgentExecutionPermission).filter(
            AgentExecutionPermission.id == agent_execution.permission_id).first()
        if agent_execution_permission.status == "PENDING":
            logger.error("handle_wait_for_permission: Permission is still pending")
            return False
        if agent_execution_permission.status == "APPROVED":
            next_step = AgentWorkflowStep.fetch_next_step(self.session, workflow_step.id, "YES")
        else:
            next_step = AgentWorkflowStep.fetch_next_step(self.session, workflow_step.id, "NO")
            result = f"{' User has given the following feedback : ' + agent_execution_permission.user_feedback if agent_execution_permission.user_feedback else ''}"


            agent_execution_feed = AgentExecutionFeed(agent_execution_id=agent_execution_permission.agent_execution_id,
                                                      agent_id=agent_execution_permission.agent_id,
                                                      feed=result, role="user",
                                                      feed_group_id=agent_execution.current_feed_group_id)
            self.session.add(agent_execution_feed)

        agent_execution.status = "RUNNING"
        agent_execution.permission_id = -1
        self.session.commit()
        self._handle_next_step(next_step)
        self.session.commit()
        return False
