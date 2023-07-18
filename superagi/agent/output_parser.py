import json
from abc import ABC, abstractmethod
from typing import Dict, NamedTuple, List
import re
import ast
import json5
from superagi.helper.json_cleaner import JsonCleaner
from superagi.lib.logger import logger


class AgentGPTAction(NamedTuple):
    name: str
    args: Dict


class AgentTasks(NamedTuple):
    tasks: List[Dict] = []
    error: str = ""


class BaseOutputParser(ABC):
    @abstractmethod
    def parse(self, text: str) -> AgentGPTAction:
        """Return AgentGPTAction"""


class AgentSchemaOutputParser(BaseOutputParser):
    def parse(self, response: str) -> AgentGPTAction:
        if response.startswith("```") and response.endswith("```"):
            response = "```".join(response.split("```")[1:-1])
        response = JsonCleaner.extract_json_section(response)
        # ast throws error if true/false params passed in json
        response = JsonCleaner.clean_boolean(response)

        # OpenAI returns `str(content_dict)`, literal_eval reverses this
        try:
            logger.debug("AgentSchemaOutputParser: ", response)
            response_obj = ast.literal_eval(response)
            return AgentGPTAction(
                name=response_obj['tool']['name'],
                args=response_obj['tool']['args'],
            )
        except BaseException as e:
            logger.info(f"AgentSchemaOutputParser: Error parsing JSON respons {e}")
            return {}
