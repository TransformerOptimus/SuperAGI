# agent has a master prompt
# agent executes the master prompt along with long term memory
# agent can run the task queue as well with long term memory
from __future__ import annotations

from pydantic import ValidationError
from pydantic.types import List
import time
from superagi.agent.agent_prompt_builder import AgentPromptBuilder
from superagi.agent.output_parser import BaseOutputParser, AgentOutputParser
from superagi.types.common import BaseMessage, HumanMessage, AIMessage, SystemMessage
from superagi.llms.base_llm import BaseLlm
from superagi.tools.base_tool import Tool
from superagi.vector_store.base import VectorStore
from superagi.vector_store.document import Document

FINISH = "finish"


class SuperAgi:
    def __init__(self,
                 ai_name: str,
                 ai_role: str,
                 llm: BaseLlm,
                 memory: VectorStore,
                 output_parser: BaseOutputParser,
                 tools: List[Tool],
                 ):
        self.ai_name = ai_name
        self.ai_role = ai_role
        self.full_message_history: List[BaseMessage] = []
        self.llm = llm
        self.memory = memory
        self.output_parser = output_parser
        self.tools = tools

    @classmethod
    def from_llm_and_tools(
            cls,
            ai_name: str,
            ai_role: str,
            memory: VectorStore,
            tools: List[Tool],
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
            "Determine which next command to use, "
            "and respond using the format specified above:"
        )
        iteration = 2
        i = 0
        while True:
            i += 1
            if i > iteration:
                return
            print(self.tools)
            autogpt_prompt = AgentPromptBuilder.get_autogpt_prompt(self.ai_name, self.ai_role, goals, self.tools)
            # generated_prompt = self.get_analytics_insight_prompt(analytics_string)
            messages = [{"role": "system", "content": autogpt_prompt},
                       {"role": "system", "content": f"The current time and date is {time.strftime('%c')}"}]

            for history in self.full_message_history[-20:]:
                messages.append({"role": history.type, "content": history.content})

            print(autogpt_prompt)
            # Discontinue if continuous limit is reached
            response = self.llm.chat_completion(messages)
            print(response)
            if response['content'] is None:
                raise RuntimeError(f"Failed to get response from llm")
            assistant_reply = response['content']

            # Print Assistant thoughts
            self.full_message_history.append(HumanMessage(content=user_input))
            self.full_message_history.append(AIMessage(content=assistant_reply))

            action = self.output_parser.parse(assistant_reply)
            tools = {t.name: t for t in self.tools}

            if action.name == FINISH:
                return action.args["response"]
            if action.name in tools:
                tool = tools[action.name]
                try:
                    observation = tool.execute(action.args)
                except ValidationError as e:
                    observation = (
                        f"Validation Error in args: {str(e)}, args: {action.args}"
                    )
                except Exception as e:
                    observation = (
                        f"Error: {str(e)}, {type(e).__name__}, args: {action.args}"
                    )
                result = f"Command {tool.name} returned: {observation}"
            elif action.name == "ERROR":
                result = f"Error: {action.args}. "
            else:
                result = (
                    f"Unknown command '{action.name}'. "
                    f"Please refer to the 'COMMANDS' list for available "
                    f"commands and only respond in the specified JSON format."
                )

            print(result)
            self.memory.add_documents([Document(text_content=assistant_reply)])
            self.full_message_history.append(SystemMessage(content=result))
        pass

    def call_llm(self):
        pass

    def move_to_next_step(self):
        pass
