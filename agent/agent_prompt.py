from typing import List


class AgentPrompt:
  def __int__(self) -> None:
    self.ai_name: str = ""
    self.ai_role: str = ""
    self.base_prompt: str = ""
    self.goals: List[str] = []
    self.constraints: List[str] = []
    self.tools: List[str] = []
    self.resources: List[str] = []
    self.evaluations: List[str] = []
    self.response_format: str = ""

  def construct_full_prompt(self) -> str:
    # Construct full prompt
    full_prompt = (
      f"You are {self.ai_name}, {self.ai_role}\n{self.base_prompt}\n\nGOALS:\n\n"
    )
    for i, goal in enumerate(self.goals):
      full_prompt += f"{i + 1}. {goal}\n"

    for i, goal in enumerate(self.goals):
      full_prompt += f"{i + 1}. {goal}\n"

    full_prompt += f"\n\n{get_prompt(self.tools)}"
    return full_prompt

  def build_agent_prompt(self):
    agent_prompt = AgentPrompt()
    prompt_start = (
      "Your decisions must always be made independently "
      "without seeking user assistance.\n"
      "Play to your strengths as an LLM and pursue simple "
      "strategies with no legal complications.\n"
      "If you have completed all your tasks, make sure to "
      'use the "finish" command.'
    )
    agent_prompt.set_base_system_prompt(prompt_start)
    agent_prompt.goals(prompt_start)




