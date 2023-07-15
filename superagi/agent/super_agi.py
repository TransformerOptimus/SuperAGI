# agent has a master prompt
# agent executes the master prompt along with long term memory
# agent can run the task queue as well with long term memory
from __future__ import annotations

import time
from typing import Any
from typing import Tuple
import json
import numpy as np
from pydantic import ValidationError
from pydantic.types import List
from sqlalchemy import asc
from sqlalchemy.orm import sessionmaker

from superagi.agent.agent_prompt_builder import AgentPromptBuilder
from superagi.agent.output_parser import BaseOutputParser, AgentOutputParser, AgentSchemaOutputParser
from superagi.agent.task_queue import TaskQueue
from superagi.apm.event_handler import EventHandler
from superagi.helper.token_counter import TokenCounter
from superagi.lib.logger import logger
from superagi.llms.base_llm import BaseLlm
from superagi.models.agent import Agent
from superagi.models.agent_execution import AgentExecution
# from superagi.models.types.agent_with_config import AgentWithConfig
from superagi.models.agent_execution_feed import AgentExecutionFeed
from superagi.models.agent_execution_permission import AgentExecutionPermission
from superagi.models.agent_workflow_step import AgentWorkflowStep
from superagi.models.db import connect_db
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
        self.full_message_history: List[BaseMessage] = []
        self.llm = llm
        self.memory = memory
        self.output_parser = output_parser
        self.tools = tools
        self.agent_config = agent_config
        self.agent_execution_config = agent_execution_config

    @classmethod
    def from_llm_and_tools(
            cls,
            ai_name: str,
            ai_role: str,
            memory: VectorStore,
            tools: List[BaseTool],
            llm: BaseLlm
    ) -> SuperAgi:
        return cls(
            ai_name=ai_name,
            ai_role=ai_role,
            llm=llm,
            memory=memory,
            output_parser=AgentOutputParser(),
            tools=tools
        )

    def fetch_agent_feeds(self, session, agent_execution_id):
        agent_feeds = session.query(AgentExecutionFeed.role, AgentExecutionFeed.feed) \
            .filter(AgentExecutionFeed.agent_execution_id == agent_execution_id) \
            .order_by(asc(AgentExecutionFeed.created_at)) \
            .all()
        return agent_feeds[2:]

    def split_history(self, history: List, pending_token_limit: int) -> Tuple[List[BaseMessage], List[BaseMessage]]:
        hist_token_count = 0
        i = len(history)
        for message in reversed(history):
            token_count = TokenCounter.count_message_tokens([{"role": message["role"], "content": message["content"]}],
                                                            self.llm.get_model())
            hist_token_count += token_count
            if hist_token_count > pending_token_limit:
                return history[:i], history[i:]
            i -= 1
        return [], history

    def execute(self, workflow_step: AgentWorkflowStep):

        session = Session()
        agent_execution_id = self.agent_config["agent_execution_id"]
        task_queue = TaskQueue(str(agent_execution_id))

        token_limit = TokenCounter.token_limit()
        agent_feeds = self.fetch_agent_feeds(session, self.agent_config["agent_execution_id"])
        current_calls = 0
        if len(agent_feeds) <= 0:
            task_queue.clear_tasks()
        messages = []
        max_token_limit = 600
        # adding history to the messages
        if workflow_step.history_enabled:
            prompt = self.build_agent_prompt(workflow_step.prompt, task_queue=task_queue,
                                             max_token_limit=max_token_limit)
            messages.append({"role": "system", "content": prompt})
            messages.append({"role": "system", "content": f"The current time and date is {time.strftime('%c')}"})
            base_token_limit = TokenCounter.count_message_tokens(messages, self.llm.get_model())
            full_message_history = [{'role': role, 'content': feed} for role, feed in agent_feeds]
            past_messages, current_messages = self.split_history(full_message_history,
                                                                 token_limit - base_token_limit - max_token_limit)
            for history in current_messages:
                messages.append({"role": history["role"], "content": history["content"]})
            messages.append({"role": "user", "content": workflow_step.completion_prompt})
        else:
            prompt = self.build_agent_prompt(workflow_step.prompt, task_queue=task_queue,
                                             max_token_limit=max_token_limit)
            messages.append({"role": "system", "content": prompt})
            # agent_execution_feed = AgentExecutionFeed(agent_execution_id=self.agent_config["agent_execution_id"],
            #                                           agent_id=self.agent_config["agent_id"], feed=template_step.prompt,
            #                                           role="user")

        logger.debug("Prompt messages:", messages)
        if len(agent_feeds) <= 0:
            for message in messages:
                agent_execution_feed = AgentExecutionFeed(agent_execution_id=self.agent_config["agent_execution_id"],
                                                          agent_id=self.agent_config["agent_id"],
                                                          feed=message["content"],
                                                          role=message["role"])
                session.add(agent_execution_feed)
                session.commit()

        current_tokens = TokenCounter.count_message_tokens(messages, self.llm.get_model())
        response = self.llm.chat_completion(messages, token_limit - current_tokens)
        current_calls = current_calls + 1
        total_tokens = current_tokens + TokenCounter.count_message_tokens(response, self.llm.get_model())

        self.update_agent_execution_tokens(current_calls, total_tokens, session)
        
        if 'content' not in response or response['content'] is None:
            raise RuntimeError(f"Failed to get response from llm")
        assistant_reply = response['content']

        final_response = {"result": "PENDING", "retry": False, "completed_task_count": 0}
        if workflow_step.output_type == "tools":
            # check if permission is required for the tool in restricted mode
            is_permission_required, response = self.check_permission_in_restricted_mode(assistant_reply, session)
            if is_permission_required:
                return response

            tool_response = self.handle_tool_response(session, assistant_reply)

            agent_execution_feed = AgentExecutionFeed(agent_execution_id=self.agent_config["agent_execution_id"],
                                                      agent_id=self.agent_config["agent_id"],
                                                      feed=assistant_reply,
                                                      role="assistant")
            session.add(agent_execution_feed)
            tool_response_feed = AgentExecutionFeed(agent_execution_id=self.agent_config["agent_execution_id"],
                                                    agent_id=self.agent_config["agent_id"],
                                                    feed=tool_response["result"],
                                                    role="system"
                                                    )
            session.add(tool_response_feed)
            final_response = tool_response
            final_response["pending_task_count"] = len(task_queue.get_tasks())
            final_response["completed_task_count"] = len(task_queue.get_completed_tasks())
        elif workflow_step.output_type == "replace_tasks":
            tasks = eval(assistant_reply)
            task_queue.clear_tasks()
            for task in reversed(tasks):
                task_queue.add_task(task)
            if len(tasks) > 0:
                logger.info("Tasks reprioritized in order: " + str(tasks))
            current_tasks = task_queue.get_tasks()
            if len(current_tasks) == 0:
                final_response = {"result": "COMPLETE", "pending_task_count": 0}
            else:
                final_response = {"result": "PENDING", "pending_task_count": len(current_tasks)}
        elif workflow_step.output_type == "tasks":
            tasks = eval(assistant_reply)
            tasks = np.array(tasks).flatten().tolist()
            for task in reversed(tasks):
                task_queue.add_task(task)
            if len(tasks) > 0:
                logger.info("Adding task to queue: " + str(tasks))
            for task in tasks:
                agent_execution_feed = AgentExecutionFeed(agent_execution_id=self.agent_config["agent_execution_id"],
                                                          agent_id=self.agent_config["agent_id"],
                                                          feed="New Task Added: " + task,
                                                          role="system")
                session.add(agent_execution_feed)
            current_tasks = task_queue.get_tasks()
            if len(current_tasks) == 0:
                final_response = {"result": "COMPLETE", "pending_task_count": 0}
            else:
                final_response = {"result": "PENDING", "pending_task_count": len(current_tasks)}
        if workflow_step.output_type == "tools" and final_response["retry"] == False:
            task_queue.complete_task(final_response["result"])
            current_tasks = task_queue.get_tasks()
            if final_response["completed_task_count"] > 0 and len(current_tasks) == 0:
                final_response["result"] = "COMPLETE"
            if len(current_tasks) > 0 and final_response["result"] == "COMPLETE":
                final_response["result"] = "PENDING"
        session.commit()

        logger.info("Iteration completed moving to next iteration!")
        session.close()
        return final_response

    def handle_tool_response(self, session, assistant_reply):
        action = self.output_parser.parse(assistant_reply)
        tools = {t.name.lower().replace(" ", ""): t for t in self.tools}
        action_name = action.name.lower().replace(" ", "")
        agent = session.query(Agent).filter(Agent.id == self.agent_config["agent_id"],).first()
        organisation = agent.get_agent_organisation(session)
        if action_name == FINISH or action.name == "":
            logger.info("\nTask Finished :) \n")
            output = {"result": "COMPLETE", "retry": False}
            EventHandler(session=session).create_event('tool_used', {'tool_name':action.name}, self.agent_config["agent_id"], organisation.id),
            return output
        if action_name in tools:
            tool = tools[action_name]
            retry = False
            EventHandler(session=session).create_event('tool_used', {'tool_name':action.name}, self.agent_config["agent_id"], organisation.id),
            try:
                parsed_args = self.clean_tool_args(action.args)
                observation = tool.execute(parsed_args)
            except ValidationError as e:
                retry = True
                observation = (
                    f"Validation Error in args: {str(e)}, args: {action.args}"
                )
            except Exception as e:
                retry = True
                observation = (
                    f"Error1: {str(e)}, {type(e).__name__}, args: {action.args}"
                )
            result = f"Tool {tool.name} returned: {observation}"
            output = {"result": result, "retry": retry}
        elif action.name == "ERROR":
            result = f"Error2: {action.args}. "
            output = {"result": result, "retry": False}
        else:
            result = (
                f"Unknown tool '{action.name}'. "
                f"Please refer to the 'TOOLS' list for available "
                f"tools and only respond in the specified JSON format."
            )
            output = {"result": result, "retry": True}

        logger.info("Tool Response : " + str(output) + "\n")
        return output

    def clean_tool_args(self, args):
        parsed_args = {}
        for key in args.keys():
            parsed_args[key] = args[key]
            if type(args[key]) is dict and "value" in args[key]:
                parsed_args[key] = args[key]["value"]
        return parsed_args


    def update_agent_execution_tokens(self, current_calls, total_tokens, session):
        agent_execution = session.query(AgentExecution).filter(
            AgentExecution.id == self.agent_config["agent_execution_id"]).first()
        agent_execution.num_of_calls += current_calls
        agent_execution.num_of_tokens += total_tokens
        session.commit()

    def build_agent_prompt(self, prompt: str, task_queue: TaskQueue, max_token_limit: int):
        pending_tasks = task_queue.get_tasks()
        completed_tasks = task_queue.get_completed_tasks()
        add_finish_tool = True
        if len(pending_tasks) > 0 or len(completed_tasks) > 0:
            add_finish_tool = False

        prompt = AgentPromptBuilder.replace_main_variables(prompt, self.agent_execution_config["goal"], self.agent_execution_config["instruction"],
                                                           self.agent_config["constraints"], self.tools, add_finish_tool)

        response = task_queue.get_last_task_details()

        last_task = ""
        last_task_result = ""
        # pending_tasks = []
        # current_task = ""
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
