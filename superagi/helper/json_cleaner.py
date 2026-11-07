import json
import re
from superagi.lib.logger import logger

import json5


class JsonCleaner:

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
        open_braces_count = cls._count_braces_outside_strings(json_string, '{')
        closed_braces_count = cls._count_braces_outside_strings(json_string, '}')

        while closed_braces_count > open_braces_count:
            json_string = json_string.rstrip("}")
            closed_braces_count -= 1

        open_braces_count = cls._count_braces_outside_strings(json_string, '{')
        closed_braces_count = cls._count_braces_outside_strings(json_string, '}')

        if open_braces_count > closed_braces_count:
            json_string += '}' * (open_braces_count - closed_braces_count)

        return json_string

    @staticmethod
    def _count_braces_outside_strings(json_string: str, brace_char: str) -> int:
        """Count occurrences of brace_char that are not inside JSON string literals.

        A naive .count() includes braces inside string values (e.g. the '}'
        in {"text": "}"}), which corrupts brace balancing. This iterates the
        string and toggles a flag on unescaped double-quotes so only
        structural braces are counted.
        """
        count = 0
        in_string = False
        escaped = False
        for ch in json_string:
            if escaped:
                escaped = False
                continue
            if ch == '\\':
                escaped = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if not in_string and ch == brace_char:
                count += 1
        return count


