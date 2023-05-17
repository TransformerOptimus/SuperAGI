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



