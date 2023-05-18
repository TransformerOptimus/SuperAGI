from abc import ABC, abstractmethod


class BaseLlm(ABC):
  @abstractmethod
  def chat_completion(self, prompt):
    pass
