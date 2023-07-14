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

class AgentOutputParser(BaseOutputParser):
    def parse(self, text: str) -> AgentGPTAction:
        try:
            logger.info(text)
            text = JsonCleaner.check_and_clean_json(text)
            parsed = json5.loads(text)
        except json.JSONDecodeError:
            return AgentGPTAction(
                name="ERROR",
                args={"error": f"Could not parse invalid json: {text}"},
            )
        try:
            format_prefix_yellow = "\033[93m\033[1m"
            format_suffix_yellow = "\033[0m\033[0m"
            format_prefix_green = "\033[92m\033[1m"
            format_suffix_green = "\033[0m\033[0m"
            logger.info(format_prefix_green + "Intelligence : " + format_suffix_green)
            if "text" in parsed["thoughts"]:
                logger.info(format_prefix_yellow + "Thoughts: " + format_suffix_yellow + parsed["thoughts"]["text"] + "\n")

            if "reasoning" in parsed["thoughts"]:
                logger.info(format_prefix_yellow + "Reasoning: " + format_suffix_yellow + parsed["thoughts"]["reasoning"] + "\n")

            if "plan" in parsed["thoughts"]:
                logger.info(format_prefix_yellow + "Plan: " + format_suffix_yellow + str(parsed["thoughts"]["plan"]) + "\n")

            if "criticism" in parsed["thoughts"]:
                logger.info(format_prefix_yellow + "Criticism: " + format_suffix_yellow + parsed["thoughts"]["criticism"] + "\n")

            logger.info(format_prefix_green + "Action : " + format_suffix_green)
            # print(format_prefix_yellow + "Args: "+ format_suffix_yellow + parsed["tool"]["args"] + "\n")
            if "tool" not in parsed:
                raise Exception("No tool found in the response..")
            if parsed["tool"] is None or not parsed["tool"]:
                return AgentGPTAction(name="", args="")
            if "name" in parsed["tool"]:
                logger.info(format_prefix_yellow + "Tool: " + format_suffix_yellow + parsed["tool"]["name"] + "\n")
            args = {}
            if "args" in parsed["tool"]:
                args = parsed["tool"]["args"]
            return AgentGPTAction(
                name=parsed["tool"]["name"],
                args=args,
            )
        except (KeyError, TypeError) as e:
            logger.error(f"Error parsing output:", e)
            # If the tool is null or incomplete, return an erroneous tool
            return AgentGPTAction(
                name="ERROR", args={"error": f"Unable to parse the output: {parsed}"}
            )

    def parse_tasks(self, text: str) -> AgentTasks:
        try:
            parsed = json.loads(text, strict=False)
        except json.JSONDecodeError:
            preprocessed_text = JsonCleaner.preprocess_json_input(text)
            try:
                parsed = json.loads(preprocessed_text, strict=False)
            except Exception:
                return AgentTasks(
                    error=f"Could not parse invalid json: {text}",
                )
        try:
            logger.info("Tasks: ", parsed["tasks"])
            return AgentTasks(
                tasks=parsed["tasks"]
            )
        except (KeyError, TypeError):
            # If the command is null or incomplete, return an erroneous tool
            return AgentTasks(
                error=f"Incomplete tool args: {parsed}",
            )