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
      print("Thoughts: ", parsed["thoughts"]["reasoning"])
      print("Reasoning: ", parsed["thoughts"]["reasoning"])
      print("Plan: ", parsed["thoughts"]["plan"])
      print("Criticism: ", parsed["thoughts"]["criticism"])
      print("Tool: ", parsed["command"]["name"])
      print("Args: ", parsed["command"]["args"])
      return AgentGPTAction(
        name=parsed["command"]["name"],
        args=parsed["command"]["args"],
      )
    except (KeyError, TypeError):
      # If the command is null or incomplete, return an erroneous tool
      return AgentGPTAction(
        name="ERROR", args={"error": f"Incomplete command args: {parsed}"}
      )
