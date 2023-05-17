from typing import List

from pydantic import BaseModel


class AgentPrompt(BaseModel):
    ai_name: str = ""
    ai_role: str = ""
    base_prompt: str = ""
    goals: List[str] = []
    constraints: List[str] = []
    tools: List[str] = []
    resources: List[str] = []
    evaluations: List[str] = []
    response_format: str = ""
