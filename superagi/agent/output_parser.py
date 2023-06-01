import json
from abc import ABC, abstractmethod
from typing import Dict, NamedTuple, List
import re

from superagi.helper.json_cleaner import JsonCleaner


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



class AgentOutputParser(BaseOutputParser):
    def parse(self, text: str) -> AgentGPTAction:
        try:
            print(text)
            text = JsonCleaner.check_and_clean_json(text)
            parsed = json.loads(text, strict=False)
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
            print(format_prefix_green + "Intelligence : " + format_suffix_green)
            if "text" in parsed["thoughts"]:
                print(format_prefix_yellow + "Thoughts: " + format_suffix_yellow + parsed["thoughts"]["text"] + "\n")
            if "reasoning" in parsed["thoughts"]:
                print(format_prefix_yellow + "Reasoning: " + format_suffix_yellow + parsed["thoughts"]["reasoning"] + "\n")

            if "plan" in parsed["thoughts"]:
                print(format_prefix_yellow + "Plan: " + format_suffix_yellow + parsed["thoughts"]["plan"] + "\n")

            if "criticism" in parsed["thoughts"]:
                print(format_prefix_yellow + "Criticism: " + format_suffix_yellow + parsed["thoughts"]["criticism"] + "\n")

            print(format_prefix_green + "Action : " + format_suffix_green)
            # print(format_prefix_yellow + "Args: "+ format_suffix_yellow + parsed["tool"]["args"] + "\n")
            if parsed["tool"] is None or not parsed["tool"]:
                return AgentGPTAction(name="", args="")
            if "name" in parsed["tool"]:
                print(format_prefix_yellow + "Tool: " + format_suffix_yellow + parsed["tool"]["name"] + "\n")
            return AgentGPTAction(
                name=parsed["tool"]["name"],
                args=parsed["tool"]["args"],
            )
        except (KeyError, TypeError):
            # If the tool is null or incomplete, return an erroneous tool
            return AgentGPTAction(
                name="ERROR", args={"error": f"Incomplete tool args: {parsed}"}
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
            print("Tasks: ", parsed["tasks"])
            return AgentTasks(
                tasks=parsed["tasks"]
            )
        except (KeyError, TypeError):
            # If the command is null or incomplete, return an erroneous tool
            return AgentTasks(
                error=f"Incomplete tool args: {parsed}",
            )


