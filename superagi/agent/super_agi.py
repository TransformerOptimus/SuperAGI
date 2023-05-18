# agent has a master prompt
# agent executes the master prompt along with long term memory
# agent can run the task queue as well with long term memory
from pydantic import ValidationError
from pydantic.types import List
import time
from superagi.agent.agent_prompt_builder import AgentPromptBuilder
from superagi.agent.output_parser import BaseOutputParser, AgentOutputParser
from superagi.agent.super_agi import SuperAgi
from superagi.common import BaseMessage, HumanMessage, AIMessage, SystemMessage
from superagi.llms.base_llm import BaseLlm
from superagi.tools.base_tool import BaseTool

FINISH = "finish"
class SuperAgi:
  def __int__(self,
              ai_name: str,
              ai_role: str,
              llm: BaseLlm,
              output_parser: BaseOutputParser,
              tools: List[BaseTool],
              ):
    self.ai_name = ai_name
    self.ai_role = ai_role
    self.full_message_history: List[BaseMessage] = []
    self.next_action_count = 0
    self.tools = tools
    self.state = None

  def from_llm_and_tools(
          cls,
          ai_name: str,
          ai_role: str,
          tools: List[BaseTool],
          llm: BaseLlm
  ) -> SuperAgi:
    autogpt_prompt = AgentPromptBuilder.get_autogpt_prompt(ai_name, ai_role, tools)
    return cls(
      llm,
      tools,
      AgentOutputParser()
    )

  def execute(self):
    user_input = (
      "Determine which next command to use, "
      "and respond using the format specified above:"
    )
    while True:
      autogpt_prompt = AgentPromptBuilder.get_autogpt_prompt(self.ai_name, self.ai_role, self.tools)
      # generated_prompt = self.get_analytics_insight_prompt(analytics_string)
      message = [{"role": "system","content": autogpt_prompt},
                 "system", f"The current time and date is {time.strftime('%c')}"]
      for history in self.full_message_history[-20:]:
        message.push({"role": history.type, "content": history.content})

      # Discontinue if continuous limit is reached
      response = self.llm.chat_completion(autogpt_prompt)
      if response.content is None:
        raise RuntimeError(f"Failed to get response from llm")
      assistant_reply = response.content

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
          observation = tool.run(action.args)
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

      self.full_message_history.append(SystemMessage(content=result))
    pass

  def call_llm(self):
    pass

  def move_to_next_step(self):
    pass
