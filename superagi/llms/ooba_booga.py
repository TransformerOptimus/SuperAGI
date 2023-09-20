from ooba_api import LlamaInstructPrompt, OobaApiClient, Parameters

from superagi.config.config import get_config
from superagi.llms.base_llm import BaseLlm

DEFAULT_MAX_MODEL_TOKEN_LIMIT = int(get_config("MAX_MODEL_TOKEN_LIMIT") or 2048)


class OobaBooga(BaseLlm):
    """
    LLM for OoobaBooga's Text Generation Web UI

    You would typically run this locally. Even though it has a web front-end, this will use the API interface
    """

    def __init__(
        self,
        model: str | None = None,
        url: str = get_config("OOBA_URL"),
        api_key: str | None = None,
        temperature: float = 0.05,
        max_tokens: int = DEFAULT_MAX_MODEL_TOKEN_LIMIT,
        top_p: float = 0.5,
        top_k: int = 4,
        typical_p: int = 1,
        repetition_penalty: float = 1.0,
        do_sample: bool = True,
        instruct: bool = True,
    ):
        self.model = model
        self.url = url
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.top_k = top_k
        self.typical_p = typical_p
        self.repetition_penalty = repetition_penalty
        self.do_sample = do_sample
        self.instruct = instruct

        assert not self.api_key, "API keys are not yet supported"
        assert self.instruct, "Non-instruct is not yet supported"

    def get_source(self) -> str:
        return "oobabooga"

    def get_model(self) -> str:
        return self.model or "ooba-booga"

    def chat_completion(
        self,
        messages: list[dict],
        max_tokens: int = DEFAULT_MAX_MODEL_TOKEN_LIMIT,
    ) -> dict[str, str]:
        """
        Do chat completion using the OoobaBooga API.

        Args:
            messages (list): The messages.
            max_tokens (int): The maximum number of tokens.

        Returns:
            dict: The response.
        """

        system_messages = []
        user_messages = []

        for message in messages:
            if message["role"] == "system":
                system_messages.append(message["content"])
            elif message["role"] == "user":
                user_messages.append(message["content"])

        system_prompt = "\n".join(system_messages)
        user_prompt = "\n".join(user_messages)

        # role does not yield right results in case of single step prompt
        if len(messages) == 1:
            user_prompt = messages[0]["content"]
        client = OobaApiClient(url=self.url)
        prompt = LlamaInstructPrompt(prompt=user_prompt, system_prompt=system_prompt)
        parameters = Parameters(
            guidance_scale=1.4,
            temperature=self.temperature,
            repetition_penalty=self.repetition_penalty,
            max_new_tokens=max_tokens,
            top_k=self.top_k,
            top_p=self.top_p,
        )
        chat_response = client.instruct(
            prompt,
            parameters,
            print_prompt=True,
        )
        return {"response": chat_response, "content": chat_response}

    def get_models(self):
        return "ooba_booga"

    def get_api_key(self) -> str:
        return self.api_key or ""

    def verify_access_key(self) -> bool:
        return True
