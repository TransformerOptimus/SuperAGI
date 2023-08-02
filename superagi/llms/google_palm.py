import google.generativeai as palm

from superagi.config.config import get_config
from superagi.lib.logger import logger
from superagi.llms.base_llm import BaseLlm


class GooglePalm(BaseLlm):
    def __init__(self, api_key, model='models/chat-bison-001', temperature=0.6, candidate_count=1, top_k=40,
                 top_p=0.95):
        """
        Args:
            api_key (str): The Google PALM API key.
            model (str): The model.
            temperature (float): The temperature.
            candidate_count (int): The number of candidates.
            top_k (int): The top k.
            top_p (float): The top p.
        """
        self.model = model
        self.temperature = temperature
        self.candidate_count = candidate_count
        self.top_k = top_k
        self.top_p = top_p
        self.api_key = api_key
        palm.configure(api_key=api_key)

    def get_source(self):
        return "google palm"

    def get_api_key(self):
        """
        Returns:
            str: The API key.
        """
        return self.api_key

    def get_model(self):
        """
        Returns:
            str: The model.
        """
        return self.model

    def chat_completion(self, messages, max_tokens=get_config("MAX_MODEL_TOKEN_LIMIT") or 800, examples=[], context=""):
        """
        Call the Google PALM chat API.

        Args:
            context (str): The context.
            examples (list): The examples.
            messages (list): The messages.

        Returns:
            dict: The response.
        """

        prompt = "\n".join(["`" + message["role"] + "`: " + message["content"] + "" for message in messages])
        # role does not yield right results in case of single step prompt
        if len(messages) == 1:
            prompt = messages[0]['content']
        try:
            # NOTE: Default chat based palm bison model has different issues. We will switch to it once it gets fixed.
            final_model = "models/text-bison-001" if self.model == "models/chat-bison-001" else self.model
            completion = palm.generate_text(
                model=final_model,
                temperature=self.temperature,
                candidate_count=self.candidate_count,
                top_k=self.top_k,
                top_p=self.top_p,
                prompt=prompt,
                max_output_tokens=int(max_tokens),
            )
            # print(completion.result)
            return {"response": completion, "content": completion.result}
        except Exception as exception:
            logger.info("Google palm Exception:", exception)
            return {"error": "ERROR_GOOGLE_PALM", "message": "Google palm exception"}

    def verify_access_key(self):
        """
        Verify the access key is valid.

        Returns:
            bool: True if the access key is valid, False otherwise.
        """
        try:
            models = palm.list_models()
            return True
        except Exception as exception:
            logger.info("Google palm Exception:", exception)
            return False

    def get_models(self):
        """
        Get the models.

        Returns:
            list: The models.
        """
        try:
            models_supported = ["chat-bison-001"]
            return models_supported
        except Exception as exception:
            logger.info("Google palm Exception:", exception)
            return []
