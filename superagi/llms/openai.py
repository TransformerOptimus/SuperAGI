import os
import json
from abc import ABC, abstractmethod

import openai
from superagi.llms.base_llm import BaseLlm
from superagi.config.config import get_config


class OpenAi(BaseLlm):
    def __init__(self, api_key, image_model=None, model="gpt-4", temperature=0.6, max_tokens=get_config("MAX_MODEL_TOKEN_LIMIT"), top_p=1,
                 frequency_penalty=0,
                 presence_penalty=0, number_of_results=1):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.number_of_results = number_of_results
        self.api_key = api_key
        self.image_model = image_model
        openai.api_key = api_key
        openai.api_base = get_config("OPENAI_API_BASE", "https://api.openai.com/v1")

    def get_model(self):
        return self.model

    def get_image_model(self):
        return self.image_model

    def chat_completion(self, messages, max_tokens=get_config("MAX_MODEL_TOKEN_LIMIT")):
        try:
            # openai.api_key = get_config("OPENAI_API_KEY")
            response = openai.ChatCompletion.create(
                n=self.number_of_results,
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=max_tokens,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty
            )
            content = response.choices[0].message["content"]
            return {"response": response, "content": content}
        except Exception as exception:
            print("Exception:", exception)
            return {"error": exception}

    def generate_image(self, prompt: str, size: int = 512, num: int = 2):
        response = openai.Image.create(
            prompt=prompt,
            n=num,
            size=f"{size}x{size}"
        )
        return response
