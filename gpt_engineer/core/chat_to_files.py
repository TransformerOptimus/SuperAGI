"""
This module provides utilities to handle and process chat content, especially for extracting code blocks
and managing them within a specified GPT Engineer project ("workspace"). It offers functionalities like parsing chat messages to
retrieve code blocks, storing these blocks into a workspace, and overwriting workspace content based on
new chat messages. Moreover, it aids in formatting and reading file content for an AI agent's input.

Key Features:
- Parse and extract code blocks from chat messages.
- Store and overwrite files within a workspace based on chat content.
- Format files to be used as inputs for AI agents.
- Retrieve files and their content based on a provided list.

Dependencies:
- `os` and `pathlib`: For handling OS-level operations and path manipulations.
- `re`: For regex-based parsing of chat content.
- `gpt_engineer.core.db`: Database handling functionalities for the workspace.
- `gpt_engineer.cli.file_selector`: Constants related to file selection.

Functions:
- parse_chat: Extracts code blocks from chat messages.
- to_files_and_memory: Saves chat content to memory and adds extracted files to a workspace.
- to_files: Adds extracted files to a workspace.
- get_code_strings: Retrieves file names and their content.
- format_file_to_input: Formats file content for AI input.
- overwrite_files_with_edits: Overwrites workspace files based on parsed edits from chat.
- apply_edits: Applies file edits to a workspace.
"""

import os
import re
import logging

from dataclasses import dataclass
from typing import List, Tuple

from gpt_engineer.data.file_repository import FileRepository, FileRepositories
from gpt_engineer.cli.file_selector import FILE_LIST_NAME


logger = logging.getLogger(__name__)


def parse_chat(chat) -> List[Tuple[str, str]]:
    """
    Extracts all code blocks from a chat and returns them
    as a list of (filename, codeblock) tuples.

    Parameters
    ----------
    chat : str
        The chat to extract code blocks from.

    Returns
    -------
    List[Tuple[str, str]]
        A list of tuples, where each tuple contains a filename and a code block.
    """
    # Get all ``` blocks and preceding filenames
    regex = r"(\S+)\n\s*```[^\n]*\n(.+?)```"
    matches = re.finditer(regex, chat, re.DOTALL)

    files = []
    for match in matches:
        # Strip the filename of any non-allowed characters and convert / to \
        path = re.sub(r'[\:<>"|?*]', "", match.group(1))

        # Remove leading and trailing brackets
        path = re.sub(r"^\[(.*)\]$", r"\1", path)

        # Remove leading and trailing backticks
        path = re.sub(r"^`(.*)`$", r"\1", path)

        # Remove trailing ]
        path = re.sub(r"[\]\:]$", "", path)

        # Get the code
        code = match.group(2)

        # Add the file to the list
        files.append((path, code))

    # Get all the text before the first ``` block
    readme = chat.split("```")[0]
    files.append(("README.md", readme))

    # Return the files
    return files


def to_files_and_memory(chat: str, dbs: FileRepositories):
    """
    Save chat to memory, and parse chat to extracted file and save them to the workspace.

    Parameters
    ----------
    chat : str
        The chat to parse.
    dbs : DBs
        The databases that include the memory and workspace database
    """
    dbs.memory["all_output.txt"] = chat
    to_files(chat, dbs.workspace)


def to_files(chat: str, workspace: FileRepository):
    """
    Parse the chat and add all extracted files to the workspace.

    Parameters
    ----------
    chat : str
        The chat to parse.
    workspace : DB
        The database containing the workspace.
    """
    files = parse_chat(chat)
    for file_name, file_content in files:
        workspace[file_name] = file_content


def get_code_strings(
    workspace: FileRepository, metadata_db: FileRepository
) -> dict[str, str]:
    """
    Read file_list.txt and return file names and their content.
    Parameters
    ----------
    input : dict
        A dictionary containing the file_list.txt.
    Returns
    -------
    dict[str, str]
        A dictionary mapping file names to their content.
    """

    files_paths = metadata_db[FILE_LIST_NAME].strip().split("\n")
    files = []

    for full_file_path in files_paths:
        if os.path.isdir(full_file_path):
            for file_path in _get_all_files_in_dir(full_file_path):
                files.append(file_path)
        else:
            files.append(full_file_path)

    files_dict = {}

    for path in files:
        assert os.path.commonpath([full_file_path, workspace.path]) == str(
            workspace.path
        ), "Trying to edit files outside of the workspace"

        file_name = os.path.relpath(path, workspace.path)

        if file_name in workspace:
            files_dict[file_name] = _open_file(path)

    return files_dict


def format_file_to_input(file_name: str, file_content: str) -> str:
    """
    Format a file string to use as input to the AI agent.

    Parameters
    ----------
    file_name : str
        The name of the file.
    file_content : str
        The content of the file.

    Returns
    -------
    str
        The formatted file string.
    """
    file_str = f"""
    {file_name}
    ```
    {file_content}
    ```
    """
    return file_str


def overwrite_files_with_edits(chat: str, dbs: FileRepositories):
    edits = parse_edits(chat)
    apply_edits(edits, dbs.workspace)


@dataclass
class Edit:
    filename: str
    before: str
    after: str


def parse_edits(llm_response):
    def parse_one_edit(lines):
        HEAD = "<<<<<<< HEAD"
        DIVIDER = "======="
        UPDATE = ">>>>>>> updated"

        filename = lines.pop(0)
        text = "\n".join(lines)
        splits = text.split(DIVIDER)
        if len(splits) != 2:
            raise ValueError(f"Could not parse following text as code edit: \n{text}")
        before, after = splits

        before = before.replace(HEAD, "").strip()
        after = after.replace(UPDATE, "").strip()

        return Edit(filename, before, after)

    def parse_all_edits(txt):
        edits = []
        current_edit = []
        in_fence = False

        for line in txt.split("\n"):
            if line.startswith("```") and in_fence:
                edits.append(parse_one_edit(current_edit))
                current_edit = []
                in_fence = False
                continue
            elif line.startswith("```") and not in_fence:
                in_fence = True
                continue

            if in_fence:
                current_edit.append(line)

        return edits

    return parse_all_edits(llm_response)


def apply_edits(edits: List[Edit], workspace: FileRepository):
    for edit in edits:
        filename = edit.filename
        if edit.before == "":
            if workspace.get(filename) is not None:
                logger.warn(
                    f"The edit to be applied wants to create a new file `{filename}`, but that already exists. The file will be overwritten. See `.gpteng/memory` for previous version."
                )
            workspace[filename] = edit.after  # new file
        else:
            occurrences_cnt = workspace[filename].count(edit.before)
            if occurrences_cnt == 0:
                logger.warn(
                    f"While applying an edit to `{filename}`, the code block to be replaced was not found. No instances will be replaced."
                )
            if occurrences_cnt > 1:
                logger.warn(
                    f"While applying an edit to `{filename}`, the code block to be replaced was found multiple times. All instances will be replaced."
                )
            workspace[filename] = workspace[filename].replace(
                edit.before, edit.after
            )  # existing file


def _get_all_files_in_dir(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            yield os.path.join(root, file)
    for dir in dirs:
        yield from _get_all_files_in_dir(os.path.join(root, dir))


def _open_file(file_path) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        raise ValueError(
            f"Non-text file detected: {file_path}, gpt-engineer currently only supports utf-8 decodable text files."
        )
