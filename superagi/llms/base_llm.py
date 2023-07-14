from abc import ABC, abstractmethod


class BaseLlm(ABC):
    @abstractmethod
    def chat_completion(self, prompt):
        pass

    @abstractmethod
    def get_source(self):
        pass

    @abstractmethod
    def get_api_key(self):
        pass

    @abstractmethod
    def get_model(self):
        pass