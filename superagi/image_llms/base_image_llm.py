from abc import ABC, abstractmethod


class BaseImageLlm(ABC):
    @abstractmethod
    def get_image_model(self):
        pass

    @abstractmethod
    def generate_image(self, prompt: str, size: int = 512, num: int = 2):
        pass
