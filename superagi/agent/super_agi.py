# agent has a master prompt
# agent executes the master prompt along with long term memory
# agent can run the task queue as well with long term memory
from __future__ import annotations

import time
from typing import Any, Dict
from typing import Tuple

from halo import Halo
from pydantic import ValidationError
from pydantic.types import List
from sqlalchemy import desc, asc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from superagi.agent.agent_prompt_builder import AgentPromptBuilder
from superagi.agent.output_parser import BaseOutputParser, AgentOutputParser
from superagi.helper.token_counter import TokenCounter
from superagi.llms.base_llm import BaseLlm
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_execution import AgentExecution
# from superagi.models.types.agent_with_config import AgentWithConfig
from superagi.models.agent_execution_feed import AgentExecutionFeed
from superagi.models.db import connectDB
from superagi.tools.base_tool import BaseTool
from superagi.types.common import BaseMessage, HumanMessage, AIMessage, SystemMessage
from superagi.vector_store.base import VectorStore
from superagi.models.agent import Agent
from superagi.models.resource import Resource
from superagi.config.config import get_config
import os

FINISH = "finish"
WRITE_FILE = "Write File"
DALLE_IMAGE_GENERATION = "Dalle Image Generation"
FILE = "FILE"
S3 = "S3"
# print("\033[91m\033[1m"
#         + "\nA bit about me...."
#         + "\033[0m\033[0m")


engine = connectDB()
Session = sessionmaker(bind=engine)
session = Session()


def make_written_file_resource(file_name: str,project_id:int):
    path = get_config("RESOURCES_OUTPUT_ROOT_DIR")
    storage_type = get_config("STORAGE_TYPE")
    file_type = "application/txt"

    root_dir = get_config('RESOURCES_OUTPUT_ROOT_DIR')

    if root_dir is not None:
        root_dir = root_dir if root_dir.startswith("/") else os.getcwd() + "/" + root_dir
        root_dir = root_dir if root_dir.endswith("/") else root_dir + "/"
        final_path = root_dir + file_name
    else:
        final_path = os.getcwd() + "/" + file_name
    file_size = os.path.getsize(final_path)
    resource = None
    if storage_type == FILE:
        # Save Resource to Database
        resource = Resource(name=file_name, path=path + "/" + file_name, storage_type=storage_type, size=file_size,
                            type=file_type,
                            channel="OUTPUT",
                            project_id=project_id)
    elif storage_type == S3:
        pass
    return resource


class SuperAgi:
    def __init__(self,
                 ai_name: str,
                 ai_role: str,
                 llm: BaseLlm,
                 memory: VectorStore,
                 tools: List[BaseTool],
                 agent_config: Any,
                 agent: Agent,
                 output_parser: BaseOutputParser = AgentOutputParser(),
                 ):
        self.ai_name = ai_name
        self.ai_role = ai_role
        self.full_message_history: List[BaseMessage] = []
        self.llm = llm
        self.memory = memory
        self.output_parser = output_parser
        self.tools = tools
        self.agent_config = agent_config
        self.agent = agent
        # Init Log
        # print("\033[92m\033[1m" + "\nWelcome to SuperAGI - The future of AGI" + "\033[0m\033[0m")

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

    def execute(self, goals: List[str]):
        user_input = (
            "Determine which next command to use, and respond using the format specified above:"
        )
        token_limit = TokenCounter.token_limit(self.llm.get_model())
        memory_window = session.query(AgentConfiguration).filter(
            AgentConfiguration.key == "memory_window",
            AgentConfiguration.agent_id == self.agent_config["agent_id"]
        ).order_by(desc(AgentConfiguration.updated_at)).first().value

        agent_feeds = session.query(AgentExecutionFeed.role, AgentExecutionFeed.feed) \
            .filter(AgentExecutionFeed.agent_execution_id == self.agent_config["agent_execution_id"]) \
            .order_by(desc(AgentExecutionFeed.created_at)) \
            .limit(memory_window) \
            .all()
        agent_feeds = reversed(agent_feeds)

        # Format the query result as a list of dictionaries
        full_message_history = [{'role': role, 'content': feed} for role, feed in agent_feeds]
        format_prefix_yellow = "\033[93m\033[1m"
        format_suffix_yellow = "\033[0m\033[0m"
        format_prefix_green = "\033[92m\033[1m"
        format_suffix_green = "\033[0m\033[0m"

        superagi_prompt = AgentPromptBuilder.get_superagi_prompt(self.ai_name, self.ai_role, goals, self.tools,
                                                                 self.agent_config)
        # print("BASE PROMPT")
        # print(superagi_prompt)
        messages = [{"role": "system", "content": superagi_prompt},
                    {"role": "system", "content": f"The current time and date is {time.strftime('%c')}"}]

        if len(full_message_history) <= 0:
            for message in messages:
                agent_execution_feed = AgentExecutionFeed(agent_execution_id=self.agent_config["agent_execution_id"],
                                                          agent_id=self.agent_config["agent_id"],
                                                          feed=message["content"],
                                                          role=message["role"])
                session.add(agent_execution_feed)
                session.commit()

        base_token_limit = TokenCounter.count_message_tokens(messages, self.llm.get_model())
        past_messages, current_messages = self.split_history(full_message_history,
                                                             token_limit - base_token_limit - 500)
        for history in current_messages:
            messages.append({"role": history["role"], "content": history["content"]})
        messages.append({"role": "user", "content": user_input})

        current_tokens = TokenCounter.count_message_tokens(messages, self.llm.get_model())

        # spinner = Halo(text='Thinking...', spinner='dots')
        # spinner.start()
        response = self.llm.chat_completion(messages, token_limit - current_tokens)
        # spinner.stop()
        print("\n")

        if response['content'] is None:
            raise RuntimeError(f"Failed to get response from llm")
        assistant_reply = response['content']

        # Print Assistant thoughts
        self.full_message_history.append(HumanMessage(content=user_input))
        agent_execution_feed = AgentExecutionFeed(agent_execution_id=self.agent_config["agent_execution_id"],
                                                  agent_id=self.agent_config["agent_id"], feed=user_input, role="user")
        session.add(agent_execution_feed)
        session.commit()

        self.full_message_history.append(AIMessage(content=assistant_reply))
        agent_execution_feed = AgentExecutionFeed(agent_execution_id=self.agent_config["agent_execution_id"],
                                                  agent_id=self.agent_config["agent_id"], feed=assistant_reply,
                                                  role="assistant")
        session.add(agent_execution_feed)
        session.commit()

        # print(assistant_reply)
        action = self.output_parser.parse(assistant_reply)
        tools = {t.name: t for t in self.tools}

        if action.name == FINISH:
            print(format_prefix_green + "\nTask Finished :) \n" + format_suffix_green)
            return "COMPLETE"
        if action.name in tools:
            tool = tools[action.name]
            print("_________________TESTING__________________")
            print(action.name)
            print(action.args)
            try:
                observation = tool.execute(action.args)
                print("Tool Observation : ")
                print(observation)
                if action.name == WRITE_FILE:
                    print("________________WRITING-FILE________________")
                    resource = make_written_file_resource(file_name=action.args.get('file_name'),
                                                          project_id=self.agent.project_id)
                    print(resource)
                    if resource is not None:
                        print("___________________RESOURCE__________")
                        session.add(resource)
                        session.commit()
                if action.name == DALLE_IMAGE_GENERATION:
                    total_images_count = action.args.get('num')
                    images = action.args.get('image_name')
                    for count in total_images_count:
                        print("________________WRITING-IMAGE________________")
                        resource = make_written_file_resource(file_name=images[count].name+f'_{count+1}',
                                                          project_id=self.agent.project_id)
                        print(resource)
                    if resource is not None:
                        print("___________________RESOURCE__________")
                        session.add(resource)
                        session.commit()
            except ValidationError as e:
                observation = (
                    f"Validation Error in args: {str(e)}, args: {action.args}"
                )
            except Exception as e:
                observation = (
                    f"Error1: {str(e)}, {type(e).__name__}, args: {action.args}"
                )
            result = f"Tool {tool.name} returned: \n {observation}"
        elif action.name == "ERROR":
            result = f"Error2: {action.args}. "
        else:
            result = (
                f"Unknown tool '{action.name}'. "
                f"Please refer to the 'TOOLS' list for available "
                f"tools and only respond in the specified JSON format."
            )

        print(format_prefix_yellow + "Tool Response : " + format_suffix_yellow + result + "\n")
        # self.memory.add_documents([Document(text_content=assistant_reply)])
        self.full_message_history.append(SystemMessage(content=result))

        agent_execution_feed = AgentExecutionFeed(agent_execution_id=self.agent_config["agent_execution_id"],
                                                  agent_id=self.agent_config["agent_id"], feed=result, role="system")
        session.add(agent_execution_feed)
        session.commit()

        print(format_prefix_green + "Iteration completed moving to next iteration!" + format_suffix_green)
        session.close()
        return "PENDING"

    def split_history(self, history: Dict, pending_token_limit: int) -> Tuple[
        List[BaseMessage], List[BaseMessage]]:
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
