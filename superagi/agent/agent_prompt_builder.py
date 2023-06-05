import json
from pydantic.types import List
from superagi.agent.agent_prompt import AgentPrompt
from superagi.tools.base_tool import BaseTool
from fastapi_sqlalchemy import db

FINISH_NAME = "finish"

class AgentPromptBuilder:
  def __init__(self,):
    self.agent_prompt = AgentPrompt()

  def set_ai_name(self, ai_name):
    self.agent_prompt.ai_name = ai_name

  def set_ai_role(self, ai_role):
    self.agent_prompt.ai_role = ai_role

  def set_base_prompt(self, base_prompt):
    self.agent_prompt.base_prompt = base_prompt

  def add_goal(self, goal):
    self.agent_prompt.goals.append(goal)

  def add_tool(self, tool):
    self.agent_prompt.tools.append(tool)

  def add_resource(self, resource: str) -> None:
    self.agent_prompt.resources.append(resource)

  def add_constraint(self, constraint):
    self.agent_prompt.constraints.append(constraint)

  def add_evaluation(self, evaluation: str) -> None:
    self.agent_prompt.evaluations.append(evaluation)

  def set_response_format(self, response_format: str) -> None:
    self.agent_prompt.response_format = response_format

  def add_list_items_to_string(self, title: str, items: List[str]) -> str:
    list_string = ""
    for i, item in enumerate(items):
      list_string += f"{i+1}. {item}\n"
    return title + ":\n" + list_string + "\n"

  def generate_prompt_string(self):
    final_string = ""
    final_string += f"I am {self.agent_prompt.ai_name}. My role is {self.agent_prompt.ai_role}\n"
    final_string += self.agent_prompt.base_prompt
    final_string += "\n"
    final_string += self.add_list_items_to_string("GOALS", self.agent_prompt.goals)
    final_string += self.add_list_items_to_string("CONSTRAINTS", self.agent_prompt.constraints)
    # commands string
    final_string = self.add_tools_to_prompt(final_string)
    final_string += self.add_list_items_to_string("RESOURCES", self.agent_prompt.resources)
    final_string += self.add_list_items_to_string("PERFORMANCE EVALUATION", self.agent_prompt.evaluations)
    final_string += f"\nI should only respond in JSON format as described below\nResponse Format:\n{self.agent_prompt.response_format}"

    final_string += "\nEnsure the response can be parsed by Python json.loads\n"
    return final_string

  def add_tools_to_prompt(self, final_string):
    final_string += "\033[91m\033[1m\nTOOLS\033[0m\033[0m:\n"
    for i, item in enumerate(self.agent_prompt.tools):
      final_string += f"{i + 1}. {self._generate_command_string(item)}\n"
    finish_description = (
      "use this to signal that you have finished all your objectives"
    )
    finish_args = (
      '"response": "final response to let '
      'people know you have finished your objectives"'
    )
    finish_string = (
      f"{len(self.agent_prompt.tools) + 1}. {FINISH_NAME}: "
      f"{finish_description}, args: {finish_args}"
    )
    final_string = final_string + finish_string + "\n\n"
    return final_string

  def _generate_command_string(self, tool: BaseTool) -> str:
    output = f"{tool.name}: {tool.description}"
    # print(tool.args)
    output += f", args json schema: {json.dumps(tool.args)}"
    return output

  @classmethod
  def get_superagi_prompt(cls, ai_name:str, ai_role: str, goals: List[str], tools: List[BaseTool], agent_config) -> str:
    # Initialize the PromptGenerator object
    prompt_builder = AgentPromptBuilder()
    prompt_builder.set_ai_name(ai_name)
    prompt_builder.set_ai_role(ai_role)

    #Base prompt is same always not fetching from DB
    base_prompt = (
      "Your decisions must always be made independently without seeking user assistance.\n"
      "Play to your strengths as an LLM and pursue simple strategies with no legal complications.\n"
      "If you have completed all your tasks, make sure to "
      'use the "finish" command.\n'
    )
    prompt_builder.set_base_prompt(base_prompt)

    # Add constraints to the PromptGenerator object


    # prompt_builder.add_constraint(
      # "~4000 word limit for short term memory. "
      # "Your short term memory is short, "
      # "so immediately save important information to files."
    # )
    # prompt_builder.add_constraint(
      # "If you are unsure how you previously did something "
      # "or want to recall past events, "
      # "thinking about similar events will help you remember."
    # )
    # prompt_builder.add_constraint("No user assistance")
    # prompt_builder.add_constraint(
    #   'Exclusively use the commands listed in double quotes e.g. "command name"'
    # )

    for constraint in agent_config["constraints"]:
      prompt_builder.add_constraint(constraint)


    # Add tools to the PromptGenerator object
    for tool in tools:
      prompt_builder.add_tool(tool)

    for goal in goals:
      prompt_builder.add_goal(goal)

    # resources = ["Internet access for searches and information gathering.",
    #              "Long Term memory management.",
    #              "GPT-3.5 powered Agents for delegation of simple tasks.",
    #              "File output."]
    # for resource in resources:
    #   prompt_builder.add_resource(resource)

    # Add performance evaluations to the PromptGenerator object
    evaluations = [
      "Continuously review and analyze your actions "
      "to ensure you are performing to the best of your abilities.",
      "Constructively self-criticize your big-picture behavior constantly.",
      "Reflect on past decisions and strategies to refine your approach.",
      "Every command has a cost, so be smart and efficient. "
      "Aim to complete tasks in the least number of steps."
    ]
    for evaluation in evaluations:
      prompt_builder.add_evaluation(evaluation)

    response_format = {
            "thoughts": {
                "text": "thought",
                "reasoning": "reasoning",
                "plan": "- short bulleted\n- list that conveys\n- long-term plan",
                "criticism": "constructive self-criticism",
                "speak": "thoughts summary to say to user",
            },
            "command": {"name": "command name/task name", "description": "command or task description", "args": {"arg name": "value"}},
        }
    formatted_response_format = json.dumps(response_format, indent=4)
    prompt_builder.set_response_format(formatted_response_format)
    # Generate the prompt string
    prompt_string = prompt_builder.generate_prompt_string()

    return prompt_string