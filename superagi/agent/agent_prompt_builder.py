from pydantic.types import List

from superagi.agent.agent_prompt import AgentPrompt
from superagi.tools.base_tool import Tool


class AgentPromptBuilder:
  def __init__(self):
    self.agent_prompt = AgentPrompt()

  def set_ai_name(self, ai_name):
    self.agent_prompt.ai_name = ai_name

  def set_ai_role(self, ai_role):
    self.agent_prompt.ai_role = ai_role

  def set_base_prompt(self, base_prompt):
    self.agent_prompt.base_prompt = base_prompt

  def add_goal(self, goal):
    self.agent_prompt.tools.append(goal)

  def add_tool(self, tool):
    self.agent_prompt.goals.append(tool)

  def add_resource(self, resource: str) -> None:
    self.agent_prompt.resources.append(resource)

  def add_constraint(self, constraint):
    self.agent_prompt.constraints.append(constraint)

  def add_evaluation(self, evaluation: str) -> None:
    self.agent_prompt.evaluations.append(evaluation)

  def set_response_format(self, response_format: str) -> None:
    self.agent_prompt.response_format = response_format

  def generate_prompt_string(self):
    final_string = ""
    final_string += f"I am {self.agent_prompt.ai_name}. My role is {self.agent_prompt.ai_role}\n"
    final_string += self.agent_prompt.base_prompt
    final_string += "\n\n"
    final_string += "Goals:\n"
    for goal in self.agent_prompt.goals:
      final_string += f"- {goal}\n"
    final_string += "\n"
    final_string += "Constraints:\n"
    for constraint in self.agent_prompt.constraints:
      final_string += f"- {constraint}\n"
    final_string += "\n"
    final_string += "Tools:\n"
    for tool in self.agent_prompt.tools:
      final_string += f"- {tool.name}\n"
    final_string += "\n"
    final_string += "Resources:\n"
    for resource in self.agent_prompt.resources:
      final_string += f"- {resource}\n"
    final_string += "\n"
    final_string += "Evaluations:\n"
    for evaluation in self.agent_prompt.evaluations:
      final_string += f"- {evaluation}\n"
    final_string += "\n"
    final_string += "Response Format:\n"
    final_string += f"- {self.agent_prompt.response_format}\n"

    final_string += "Ensure the response can be parsed by Python json.loads\n"
    return final_string

  @classmethod
  def get_autogpt_prompt(cls, ai_name:str, ai_role: str, tools: List[Tool]) -> str:
    # Initialize the PromptGenerator object
    prompt_builder = AgentPromptBuilder()
    prompt_builder.set_ai_name(ai_name)
    prompt_builder.set_ai_role(ai_role)
    base_prompt = (
      "Your decisions must always be made independently "
      "without seeking user assistance.\n"
      "Play to your strengths as an LLM and pursue simple "
      "strategies with no legal complications.\n"
      "If you have completed all your tasks, make sure to "
      'use the "finish" command.'
    )
    prompt_builder.set_base_prompt(base_prompt)

    # Add constraints to the PromptGenerator object
    prompt_builder.add_constraint(
      "~4000 word limit for short term memory. "
      "Your short term memory is short, "
      "so immediately save important information to files."
    )
    prompt_builder.add_constraint(
      "If you are unsure how you previously did something "
      "or want to recall past events, "
      "thinking about similar events will help you remember."
    )
    prompt_builder.add_constraint("No user assistance")
    prompt_builder.add_constraint(
      'Exclusively use the commands listed in double quotes e.g. "command name"'
    )

    # Add commands to the PromptGenerator object
    for tool in tools:
      prompt_builder.add_tool(tool)

    resources = ["Internet access for searches and information gathering.",
                 "Long Term memory management.",
                 "GPT-3.5 powered Agents for delegation of simple tasks.",
                 "File output."]
    for resource in resources:
      prompt_builder.add_resource(resource)

    # Add performance evaluations to the PromptGenerator object
    evaluations = [
      "Continuously review and analyze your actions "
      "to ensure you are performing to the best of your abilities.",
      "Constructively self-criticize your big-picture behavior constantly.",
      "Reflect on past decisions and strategies to refine your approach.",
      "Every command has a cost, so be smart and efficient. "
      "Aim to complete tasks in the least number of steps.",
    ]
    for evaluation in evaluations:
      prompt_builder.add_evaluation(evaluation)

    # Generate the prompt string
    prompt_string = prompt_builder.generate_prompt_string()

    return prompt_string
