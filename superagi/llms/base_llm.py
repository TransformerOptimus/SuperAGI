from abc import ABC, abstractmethod


class BaseLlm(ABC):
  @abstractmethod
  async def chat_completion(self, prompt):
    pass
