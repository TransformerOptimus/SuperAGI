from abc import ABC, abstractmethod


class BaseEmbedding(ABC):

    @abstractmethod
    def get_embedding(self, text):
        pass
