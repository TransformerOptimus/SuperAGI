# agent has a master prompt
# agent executes the master prompt along with long term memory
# agent can run the task queue as well with long term memory
from __future__ import annotations

from pydantic import ValidationError
from pydantic.types import List
import time
from superagi.agent.agent_prompt_builder import AgentPromptBuilder
from superagi.agent.agent_prompt_to_print_builder import AgentPromptToPrintBuilder
from superagi.agent.output_parser import BaseOutputParser, AgentOutputParser
from superagi.helper.token_counter import TokenCounter
from superagi.types.common import BaseMessage, HumanMessage, AIMessage, SystemMessage
from superagi.llms.base_llm import BaseLlm
from superagi.tools.base_tool import BaseTool
from superagi.vector_store.base import VectorStore
from superagi.vector_store.document import Document
import json
# from spinners.spinners import Spinner
# from spinners import Spinners #Enum
from halo import Halo




FINISH = "finish"
print("\033[92m\033[1m" + "\nWelcome to SuperAGI - The future of AGI" + "\033[0m\033[0m")
# print("\033[91m\033[1m"
#         + "\nA bit about me...."
#         + "\033[0m\033[0m")

class SuperAgi:
    def __init__(self,
                 ai_name: str,
                 ai_role: str,
                 llm: BaseLlm,
                 memory: VectorStore,
                 output_parser: BaseOutputParser,
                 tools: List[BaseTool],
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
            "Determine which next command to use, "
            "and respond using the format specified above:"
        )
        iteration = 10
        i = 0
        while True:
            format_prefix_yellow = "\033[93m\033[1m"
            format_suffix_yellow = "\033[0m\033[0m"
            format_prefix_green = "\033[92m\033[1m"
            format_suffix_green = "\033[0m\033[0m"
            i += 1
            print("\n"+format_prefix_green + "____________________Iteration : "+str(i)+"________________________" + format_suffix_green+"\n")            
            if i > iteration:
                return
            # print(self.tools)
            autogpt_prompt = AgentPromptBuilder.get_autogpt_prompt(self.ai_name, self.ai_role, goals, self.tools)
            autogpt_prompt_to_print = AgentPromptToPrintBuilder.get_autogpt_prompt(self.ai_name, self.ai_role, goals, self.tools)
            # generated_prompt = self.get_analytics_insight_prompt(analytics_string)
            messages = [{"role": "system", "content": autogpt_prompt},
                       {"role": "system", "content": f"The current time and date is {time.strftime('%c')}"}]

            for history in self.full_message_history[-10:]:
                # print(history.type + " : ", history.content)
                messages.append({"role": history.type, "content": history.content})

            # print(autogpt_prompt)
            print(autogpt_prompt_to_print)
            # Discontinue if continuous limit is reached
            current_tokens = TokenCounter.count_message_tokens(messages, self.llm.get_model())
            token_limit = TokenCounter.token_limit(self.llm.get_model())

            # spinner = Spinners.dots12
            # spinner.start()
            # spinner = Spinner('dots12')
            # spinner.start()


            # print("Token remaining:", token_limit - current_tokens)
            # print(Spinners.line)
            spinner = Halo(text='Thinking...', spinner='dots')
            spinner.start()
            response = self.llm.chat_completion(messages, token_limit - current_tokens)
            spinner.stop()
            # parsed_response = json.loads(response['choices'][0]['message']['content'])
            # parsed_response = json.loads(response)
            
            # Print the formatted response
            # formatted_response = json.dumps(response, indent=4)
            # formatted_response = json.dumps(response['choices'],indent=4)

            # print(response['choices'])
            # print(response['content'])
            print("\n")

            if response['content'] is None:
                raise RuntimeError(f"Failed to get response from llm")
            assistant_reply = response['content']

            # Print Assistant thoughts
            self.full_message_history.append(HumanMessage(content=user_input))
            self.full_message_history.append(AIMessage(content=assistant_reply))

            # print(assistant_reply)
            action = self.output_parser.parse(assistant_reply)
            tools = {t.name: t for t in self.tools}

            if action.name == FINISH:
                print(format_prefix_green + "\nTask Finished :) \n" + format_suffix_green)
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
                        f"Error1: {str(e)}, {type(e).__name__}, args: {action.args}"
                    )
                result = f"Tool {tool.name} returned: {observation}"
            elif action.name == "ERROR":
                result = f"Error2: {action.args}. "
            else:
                result = (
                    f"Unknown tool '{action.name}'. "
                    f"Please refer to the 'TOOLS' list for available "
                    f"tools and only respond in the specified JSON format."
                )

            print(format_prefix_yellow + "Tool Response : " + format_suffix_yellow + result + "\n")
            #self.memory.add_documents([Document(text_content=assistant_reply)])
            self.full_message_history.append(SystemMessage(content=result))
            # print(self.full_message_history)
            
            print(format_prefix_green + "Interation completed moving to next iteration!" + format_suffix_green)
        pass

    def call_llm(self):
        pass

    def move_to_next_step(self):
        pass
