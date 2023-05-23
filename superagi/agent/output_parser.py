import json
from abc import ABC, abstractmethod
from typing import Dict, NamedTuple
import re

class AgentGPTAction(NamedTuple):
  name: str
  args: Dict


class BaseOutputParser(ABC):
  @abstractmethod
  def parse(self, text: str) -> AgentGPTAction:
    """Return AgentGPTAction"""


def preprocess_json_input(input_str: str) -> str:
  # Replace single backslashes with double backslashes,
  # while leaving already escaped ones intact
  corrected_str = re.sub(
    r'(?<!\\)\\(?!["\\/bfnrt]|u[0-9a-fA-F]{4})', r"\\\\", input_str
  )
  return corrected_str


class AgentOutputParser(BaseOutputParser):
  def parse(self, text: str) -> AgentGPTAction:
    try:
      parsed = json.loads(text, strict=False)
    except json.JSONDecodeError:
      preprocessed_text = preprocess_json_input(text)
      try:
        parsed = json.loads(preprocessed_text, strict=False)
      except Exception:
        return AgentGPTAction(
          name="ERROR",
          args={"error": f"Could not parse invalid json: {text}"},
        )
    try:
      format_prefix_yellow = "\033[93m\033[1m"
      format_suffix_yellow = "\033[0m\033[0m"
      format_prefix_green = "\033[92m\033[1m"
      format_suffix_green = "\033[0m\033[0m"
      print(format_prefix_green  + "Intelligence : " + format_suffix_green)
      print(format_prefix_yellow + "Thoughts: " + format_suffix_yellow + parsed["thoughts"]["reasoning"]+"\n")
      print(format_prefix_yellow + "Reasoning: " + format_suffix_yellow + parsed["thoughts"]["reasoning"] + "\n")
      print(format_prefix_yellow + "Plan: " + format_suffix_yellow + parsed["thoughts"]["plan"] + "\n")
      print(format_prefix_yellow + "Criticism: " + format_suffix_yellow + parsed["thoughts"]["criticism"] + "\n")
      print(format_prefix_green  + "Action : "+ format_suffix_green)
      print(format_prefix_yellow + "Tool: "+ format_suffix_yellow +  parsed["command"]["name"] + "\n")
      # print(format_prefix_yellow + "Args: "+ format_suffix_yellow + parsed["command"]["args"] + "\n")
      return AgentGPTAction(
        name=parsed["command"]["name"],
        args=parsed["command"]["args"],
      )
    except (KeyError, TypeError):
      # If the command is null or incomplete, return an erroneous tool
      return AgentGPTAction(
        name="ERROR", args={"error": f"Incomplete command args: {parsed}"}
      )
