from abc import ABC, abstractmethod


class BaseLlm(ABC):
    @abstractmethod
    def chat_completion(self, prompt):
        pass

    @abstractmethod
    def get_model(self):
        pass

    @abstractmethod
    def get_image_model(self):
        pass

    @abstractmethod
    def generate_image(self, prompt: str, size: int = 512, num: int = 2):
        pass
