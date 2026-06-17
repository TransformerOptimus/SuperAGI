import ast
import json
import re
from superagi.lib.logger import logger

import json5


class JsonCleaner:

    @classmethod
    def parse_array_section(cls, input_str: str = ""):
        """
        Safely parse the array section of an LLM reply into a Python list.

        This is the safe replacement for ``eval()`` on model output. Model
        replies are only ever expected to contain a literal array of task
        strings (e.g. ``["task1", "task2"]`` or, because OpenAI emits
        ``str(dict)``-style payloads, single-quoted ``['task1', 'task2']``).
        ``ast.literal_eval`` accepts both quoting styles but, unlike ``eval``,
        evaluates *only* Python literals, so it can never execute function
        calls, imports or other code embedded in the reply
        (e.g. ``[__import__('os').system('id')]`` raises instead of running).

        Args:
            input_str (str): The (already array-sliced) model reply.

        Returns:
            list: The parsed list of tasks.

        Raises:
            ValueError: If the input is not a literal Python/JSON list.
        """
        array_section = cls.extract_json_array_section(input_str)
        try:
            parsed = ast.literal_eval(array_section)
        except (ValueError, SyntaxError, TypeError, MemoryError, RecursionError):
            logger.error("JsonCleaner.parse_array_section: unable to parse array section safely")
            raise ValueError("Model reply did not contain a valid literal array")
        if not isinstance(parsed, (list, tuple)):
            raise ValueError("Model reply did not contain a valid literal array")
        return list(parsed)

    @classmethod
    def clean_boolean(cls, input_str: str = ""):
        """
        Clean the boolean values in the given string.

        Args:
            input_str (str): The string from which the json section is to be extracted.

        Returns:
            str: The extracted json section.
        """
        input_str = re.sub(r':\s*false', ': False', input_str)
        input_str = re.sub(r':\s*true', ': True', input_str)
        return input_str


    @classmethod
    def extract_json_section(cls, input_str: str = ""):
        """
        Extract the json section from the given string.

        Args:
            input_str (str): The string from which the json section is to be extracted.

        Returns:
            str: The extracted json section.
        """
        try:
            first_brace_index = input_str.index("{")
            final_json = input_str[first_brace_index:]
            last_brace_index = final_json.rindex("}")
            final_json = final_json[: last_brace_index + 1]
            return final_json
        except ValueError:
            pass
        return input_str

    @classmethod
    def extract_json_array_section(cls, input_str: str = ""):
        """
        Extract the json section from the given string.

        Args:
            input_str (str): The string from which the json section is to be extracted.

        Returns:
            str: The extracted json section.
        """
        try:
            first_brace_index = input_str.index("[")
            final_json = input_str[first_brace_index:]
            last_brace_index = final_json.rindex("]")
            final_json = final_json[: last_brace_index + 1]
            return final_json
        except ValueError:
            pass
        return input_str

    @classmethod
    def remove_escape_sequences(cls, string):
        """
        Remove escape sequences from the given string.

        Args:
            string (str): The string from which the escape sequences are to be removed.

        Returns:
            str: The string with escape sequences removed.
        """
        return string.encode('utf-8').decode('unicode_escape').encode('raw_unicode_escape').decode('utf-8')

    @classmethod
    def balance_braces(cls, json_string: str) -> str:
        """
        Balance the braces in the given json string.

        Args:
            json_string (str): The json string to be processed.

        Returns:
            str: The json string with balanced braces.
        """
        open_braces_count = json_string.count('{')
        closed_braces_count = json_string.count('}')

        while closed_braces_count > open_braces_count:
            json_string = json_string.rstrip("}")
            closed_braces_count -= 1

        open_braces_count = json_string.count('{')
        closed_braces_count = json_string.count('}')

        if open_braces_count > closed_braces_count:
            json_string += '}' * (open_braces_count - closed_braces_count)

        return json_string


