# agent has a master prompt
# agent executes the master prompt along with long term memory
# agent can run the task queue as well with long term memory
from __future__ import annotations

import time
from typing import Any
from typing import Tuple

from pydantic.types import List
from sqlalchemy import asc
from sqlalchemy.orm import sessionmaker

from superagi.agent.agent_message_builder import AgentLlmMessageBuilder
from superagi.agent.agent_prompt_builder import AgentPromptBuilder
from superagi.agent.output_handler import ToolOutputHandler, ReplaceTaskOutputHandler, TaskOutputHandler
from superagi.agent.output_parser import BaseOutputParser, AgentSchemaOutputParser
from superagi.agent.task_queue import TaskQueue
from superagi.agent.tool_executor import ToolExecutor
from superagi.config.config import get_config
from superagi.helper.token_counter import TokenCounter
from superagi.lib.logger import logger
from superagi.llms.base_llm import BaseLlm
from superagi.models.agent import Agent
from superagi.models.agent_execution import AgentExecution
# from superagi.models.types.agent_with_config import AgentWithConfig
from superagi.models.agent_execution_feed import AgentExecutionFeed
from superagi.models.agent_execution_permission import AgentExecutionPermission
from superagi.models.db import connect_db
from superagi.models.workflows.agent_workflow_step import AgentWorkflowStep
from superagi.tools.base_tool import BaseTool
from superagi.types.common import BaseMessage
from superagi.vector_store.base import VectorStore

FINISH = "finish"
WRITE_FILE = "Write File"
FILE = "FILE"
S3 = "S3"
# print("\033[91m\033[1m"
#         + "\nA bit about me...."
#         + "\033[0m\033[0m")


engine = connect_db()
Session = sessionmaker(bind=engine)


class SuperAgi:
    def __init__(self,
                 ai_name: str,
                 ai_role: str,
                 llm: BaseLlm,
                 memory: VectorStore,
                 tools: List[BaseTool],
                 agent_config: Any,
                 agent_execution_config: Any,
                 output_parser: BaseOutputParser = AgentSchemaOutputParser(),
                 ):
        self.ai_name = ai_name
        self.ai_role = ai_role
        self.llm = llm
        self.memory = memory
        self.output_parser = output_parser
        self.tools = tools
        self.agent_config = agent_config
        self.agent_execution_config = agent_execution_config


    def fetch_agent_feeds(self, session, agent_execution_id):
        agent_feeds = session.query(AgentExecutionFeed.role, AgentExecutionFeed.feed) \
            .filter(AgentExecutionFeed.agent_execution_id == agent_execution_id) \
            .order_by(asc(AgentExecutionFeed.created_at)) \
            .all()
        return agent_feeds[2:]


    def execute(self, workflow_step: AgentWorkflowStep):
        session = Session()
        agent_execution_id = self.agent_config["agent_execution_id"]
        task_queue = TaskQueue(str(agent_execution_id))

        execution = AgentExecution.find_by_id(session, agent_execution_id)
        agent_feeds = self.fetch_agent_feeds(session, execution.id)
        if not agent_feeds:
            task_queue.clear_tasks()
        # adding history to the messages
        prompt = self.build_agent_prompt(workflow_step.prompt, task_queue=task_queue,
                                         max_token_limit=int(get_config("MAX_TOOL_TOKEN_LIMIT", 600)))

        messages = AgentLlmMessageBuilder(session, self.llm.get_model(), execution.agent_id, execution.id) \
            .build_agent_messages(prompt, agent_feeds, history_enabled=workflow_step.history_enabled,
                                  completion_prompt=workflow_step.completion_prompt)
        # adding history to the messages

        logger.debug("Prompt messages:", messages)
        current_tokens = TokenCounter.count_message_tokens(messages, self.llm.get_model())
        response = self.llm.chat_completion(messages, TokenCounter.token_limit(self.llm.get_model()) - current_tokens)
        total_tokens = current_tokens + TokenCounter.count_message_tokens(response, self.llm.get_model())

        AgentExecution.update_tokens(session, agent_execution_id, total_tokens)
        
        if 'content' not in response or response['content'] is None:
            raise RuntimeError(f"Failed to get response from llm")
        assistant_reply = response['content']

        final_response = {"result": "PENDING", "retry": False, "completed_task_count": 0}
        if workflow_step.output_type == "tools":
            final_response = ToolOutputHandler(agent_execution_id, self.agent_config).handle(session, assistant_reply)
        elif workflow_step.output_type == "replace_tasks":
            final_response = ReplaceTaskOutputHandler(agent_execution_id).handle(session,
                                                                                                      assistant_reply)
        elif workflow_step.output_type == "tasks":
            final_response = TaskOutputHandler(agent_execution_id).handle(session, assistant_reply,
                                                                                               task_queue)
        final_response["pending_task_count"] = len(task_queue.get_tasks())
        final_response["completed_task_count"] = len(task_queue.get_completed_tasks())
        session.commit()

        logger.info("Iteration completed moving to next iteration!")
        session.close()
        return final_response

    def build_agent_prompt(self, prompt: str, task_queue: TaskQueue, max_token_limit: int):
        pending_tasks = task_queue.get_tasks()
        completed_tasks = task_queue.get_completed_tasks()
        add_finish_tool = True
        if pending_tasks or completed_tasks:
            add_finish_tool = False

        prompt = AgentPromptBuilder.replace_main_variables(prompt, self.agent_execution_config["goal"], self.agent_execution_config["instruction"],
                                                           self.agent_config["constraints"], self.tools, add_finish_tool)

        response = task_queue.get_last_task_details()

        last_task, last_task_result = "", ""
        if response is not None:
            last_task = response["task"]
            last_task_result = response["response"]
        current_task = task_queue.get_first_task() or ""
        token_limit = TokenCounter.token_limit() - max_token_limit
        prompt = AgentPromptBuilder.replace_task_based_variables(prompt, current_task, last_task, last_task_result,
                                                                 pending_tasks, completed_tasks, token_limit)
        return prompt

    def check_permission_in_restricted_mode(self, assistant_reply: str, session):
        action = self.output_parser.parse(assistant_reply)
        tools = {t.name: t for t in self.tools}

        excluded_tools = [FINISH, '', None]

        if self.agent_config["permission_type"].upper() == "RESTRICTED" and action.name not in excluded_tools and \
                tools.get(action.name) and tools[action.name].permission_required:
            new_agent_execution_permission = AgentExecutionPermission(
                agent_execution_id=self.agent_config["agent_execution_id"],
                status="PENDING",
                agent_id=self.agent_config["agent_id"],
                tool_name=action.name,
                assistant_reply=assistant_reply)

            session.add(new_agent_execution_permission)
            session.commit()
            return True, {"result": "WAITING_FOR_PERMISSION", "permission_id": new_agent_execution_permission.id}
        return False, None



