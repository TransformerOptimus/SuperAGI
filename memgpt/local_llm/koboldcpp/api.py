import os
from urllib.parse import urljoin
import requests

from .settings import SIMPLE
from ..utils import load_grammar_file, count_tokens

HOST = os.getenv("OPENAI_API_BASE")
HOST_TYPE = os.getenv("BACKEND_TYPE")  # default None == ChatCompletion
KOBOLDCPP_API_SUFFIX = "/api/v1/generate"
# DEBUG = False
DEBUG = True


def get_koboldcpp_completion(prompt, context_window, grammar=None, settings=SIMPLE):
    """See https://lite.koboldai.net/koboldcpp_api for API spec"""
    prompt_tokens = count_tokens(prompt)
    if prompt_tokens > context_window:
        raise Exception(f"Request exceeds maximum context length ({prompt_tokens} > {context_window} tokens)")

    # Settings for the generation, includes the prompt + stop tokens, max length, etc
    request = settings
    request["prompt"] = prompt
    request["max_context_length"] = context_window

    # Set grammar
    if grammar is not None:
        request["grammar"] = load_grammar_file(grammar)

    if not HOST.startswith(("http://", "https://")):
        raise ValueError(f"Provided OPENAI_API_BASE value ({HOST}) must begin with http:// or https://")

    try:
        # NOTE: llama.cpp server returns the following when it's out of context
        # curl: (52) Empty reply from server
        URI = urljoin(HOST.strip("/") + "/", KOBOLDCPP_API_SUFFIX.strip("/"))
        response = requests.post(URI, json=request)
        if response.status_code == 200:
            result = response.json()
            result = result["results"][0]["text"]
            if DEBUG:
                print(f"json API response.text: {result}")
        else:
            raise Exception(
                f"API call got non-200 response code (code={response.status_code}, msg={response.text}) for address: {URI}."
                + f" Make sure that the koboldcpp server is running and reachable at {URI}."
            )

    except:
        # TODO handle gracefully
        raise

    return result
