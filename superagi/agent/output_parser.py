import json
from abc import ABC, abstractmethod
from typing import Dict, NamedTuple, List, Optional
import re
import ast
import json
from superagi.helper.json_cleaner import JsonCleaner
from superagi.lib.logger import logger


class ParsingError(Exception):
    """Raised when output parsing fails"""
    pass


class AgentGPTAction(NamedTuple):
    name: str
    args: Dict


class AgentTasks(NamedTuple):
    tasks: List[str] = []
    error: str = ""


class BaseOutputParser(ABC):
    """Base class for parsing agent outputs"""
    
    @abstractmethod
    def parse(self, text: str) -> AgentGPTAction:
        """Parse AI model output and return AgentGPTAction
        
        Args:
            text: The raw AI model response text
            
        Returns:
            AgentGPTAction: Parsed action with name and arguments
            
        Raises:
            ParsingError: If the output cannot be parsed
        """
        pass
    
    def validate_response(self, response: str) -> bool:
        """Validate response format before parsing
        
        Args:
            response: The response text to validate
            
        Returns:
            bool: True if response is valid
        """
        if not response or not isinstance(response, str):
            return False
        return True


class AgentSchemaOutputParser(BaseOutputParser):
    """Parses the output from the agent schema with enhanced error handling"""
    
    def parse(self, response: str) -> AgentGPTAction:
        """Parse agent schema response into AgentGPTAction
        
        Args:
            response: Raw AI model response
            
        Returns:
            AgentGPTAction: Parsed action
            
        Raises:
            ParsingError: If response cannot be parsed
        """
        if not self.validate_response(response):
            raise ParsingError("Invalid response format: empty or not a string")
        
        if response.startswith("```") and response.endswith("```"):
            response = "```".join(response.split("```")[1:-1])
        response = JsonCleaner.extract_json_section(response)
        # ast throws error if true/false params passed in json
        response = JsonCleaner.clean_boolean(response)

        # OpenAI returns `str(content_dict)`, literal_eval reverses this
        try:
            logger.debug("AgentSchemaOutputParser: parsing response")
            response_obj = ast.literal_eval(response)
            
            # Validate required fields
            if 'tool' not in response_obj or 'name' not in response_obj['tool']:
                raise ParsingError("Response missing required 'tool.name' field")
            
            args = response_obj['tool'].get('args', {})
            return AgentGPTAction(
                name=response_obj['tool']['name'],
                args=args,
            )
        except ParsingError:
            raise
        except ValueError as e:
            logger.error(f"AgentSchemaOutputParser: Invalid JSON format - {e}")
            raise ParsingError(f"Invalid JSON format: {e}")
        except KeyError as e:
            logger.error(f"AgentSchemaOutputParser: Missing required field - {e}")
            raise ParsingError(f"Missing required field: {e}")
        except Exception as e:
            logger.error(f"AgentSchemaOutputParser: Unexpected error parsing response - {e}")
            raise ParsingError(f"Failed to parse response: {e}")


class AgentSchemaToolOutputParser(BaseOutputParser):
    """Parses the output from the agent schema for the tool"""
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
            args = response_obj['args'] if 'args' in response_obj else {}
            return AgentGPTAction(
                name=response_obj['name'],
                args=args,
            )
        except BaseException as e:
            logger.info(f"AgentSchemaToolOutputParser: Error parsing JSON response {e}")
            raise e
