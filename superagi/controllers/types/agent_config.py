from typing import Union
from pydantic import BaseModel

class AgentConfig(BaseModel):
    agent_id: int
    key: str
    value: Union[str, list]

    def __repr__(self):
        return f"AgentConfiguration(id={self.id}, key={self.key}, value={self.value})"

