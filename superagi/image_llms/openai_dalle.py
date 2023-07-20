import openai

from superagi.config.config import get_config
from superagi.image_llms.base_image_llm import BaseImageLlm


class OpenAiDalle(BaseImageLlm):
    def __init__(self, api_key, image_model=None, number_of_results=1):
        """
        Args:
            api_key (str): The OpenAI API key.
            image_model (str): The image model.
            number_of_results (int): The number of results.
        """
        self.number_of_results = number_of_results
        self.api_key = api_key
        self.image_model = image_model
        openai.api_key = api_key
        openai.api_base = get_config("OPENAI_API_BASE", "https://api.openai.com/v1")

    def get_image_model(self):
        """
        Returns:
            str: The image model.
        """
        return self.image_model

    def generate_image(self, prompt: str, size: int = 512):
        """
        Call the OpenAI image API.

        Args:
            prompt (str): The prompt.
            size (int): The size.
            num (int): The number of images.

        Returns:
            dict: The response.
        """
        response = openai.Image.create(
            prompt=prompt,
            n=self.number_of_results,
            size=f"{size}x{size}"
        )
        return response
