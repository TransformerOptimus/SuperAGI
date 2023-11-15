"""
GPT Engineer workflow definition and execution

This module provides the necessary utilities and functions to orchestrate the execution of GPT-engineer's tasks
related to code generation, execution, and review. It leverages a flexible approach to system prompt creation,
workflow execution, and interaction with AI, allowing for various configurations and stages of operation.

Imports:
- Standard libraries: inspect, re, subprocess
- Additional libraries/packages: termcolor, typing, enum
- Internal modules/packages: langchain.schema, gpt_engineer.core, gpt_engineer.cli

Key Features:
- Dynamic system prompt creation for both new code generation and improving existing code.
- A series of utility functions for handling various tasks like AI code generation, user clarification,
  code execution, and human review.
- Configurable workflow steps to control the process of code generation and execution in different scenarios.
- Flexibility to adapt to different configurations and use cases.

Classes:
- Config: An enumeration representing different configurations or operation modes for the workflow.

Functions:
- setup_sys_prompt(dbs: FileRepositories) -> str: Creates a system prompt for the AI.
- setup_sys_prompt_existing_code(dbs: FileRepositories) -> str: System prompt creation using existing code base.
- curr_fn() -> str: Returns the name of the current function.
- lite_gen(ai: AI, dbs: FileRepositories) -> List[Message]: Runs the AI on the main prompt and saves results.
- simple_gen(ai: AI, dbs: FileRepositories) -> List[Message]: Runs the AI on default prompts and saves results.
- clarify(ai: AI, dbs: FileRepositories) -> List[Message]: Interacts with the user for clarification.
- gen_clarified_code(ai: AI, dbs: FileRepositories) -> List[dict]: Generates code after clarification.
- execute_entrypoint(ai: AI, dbs: FileRepositories) -> List[dict]: Executes code entry point and asks user for confirmation.
- gen_entrypoint(ai: AI, dbs: FileRepositories) -> List[dict]: Generates entry point based on information about a codebase.
- use_feedback(ai: AI, dbs: FileRepositories): Uses feedback from users to improve code.
- set_improve_filelist(ai: AI, dbs: FileRepositories): Sets the file list for existing code improvements.
- assert_files_ready(ai: AI, dbs: FileRepositories): Checks for the required files for code improvement.
- get_improve_prompt(ai: AI, dbs: FileRepositories): Interacts with the user to know what they want to fix in existing code.
- improve_existing_code(ai: AI, dbs: FileRepositories): Generates improved code after getting the file list and user prompt.
- human_review(ai: AI, dbs: FileRepositories): Collects and stores human review of the generated code.

Constants:
- STEPS: A dictionary that maps the Config enum to lists of functions to execute for each configuration.

Note:
- This module is central to the GPT-engineer system and its functions are intended to be used in orchestrated
  workflows. As such, it should be used carefully, with attention to the correct order and sequence of operations.
"""

import inspect
import re
import subprocess

from enum import Enum
from platform import platform
from sys import version_info
from typing import List, Union

from langchain.schema import AIMessage, HumanMessage, SystemMessage
from termcolor import colored
from pathlib import Path

from gpt_engineer.core.ai import AI
from gpt_engineer.core.chat_to_files import (
    format_file_to_input,
    get_code_strings,
    overwrite_files_with_edits,
    to_files_and_memory,
)
from gpt_engineer.data.file_repository import FileRepositories
from gpt_engineer.cli.file_selector import FILE_LIST_NAME, ask_for_files
from gpt_engineer.cli.learning import human_review_input
from gpt_engineer.data.code_vector_repository import CodeVectorRepository

MAX_SELF_HEAL_ATTEMPTS = 2  # constants for self healing code
ASSUME_WORKING_TIMEOUT = 30

# Type hint for chat messages
Message = Union[AIMessage, HumanMessage, SystemMessage]


def get_platform_info():
    """Returns the Platform: OS, and the Python version.
    This is used for self healing.  There are some possible areas of conflict here if
    you use a different version of Python in your virtualenv.  A better solution would
    be to have this info printed from the virtualenv.
    """
    v = version_info
    a = f"Python Version: {v.major}.{v.minor}.{v.micro}"
    b = f"\nOS: {platform()}\n"
    return a + b


def get_platform_info():
    """Returns the Platform: OS, and the Python version.
    This is used for self healing.  There are some possible areas of conflict here if
    you use a different version of Python in your virtualenv.  A better solution would
    be to have this info printed from the virtualenv.
    """
    v = version_info
    a = f"Python Version: {v.major}.{v.minor}.{v.micro}"
    b = f"\nOS: {platform()}\n"
    return a + b


def setup_sys_prompt(dbs: FileRepositories) -> str:
    """
    Constructs a system prompt for the AI based on predefined instructions and philosophies.

    This function is responsible for setting up the system prompts for the AI, instructing
    it on how to generate code and the coding philosophy to adhere to. The constructed prompt
    consists of the "roadmap", "generate" (with dynamic format replacements), and the coding
    "philosophy" taken from the given DBs object.

    Parameters:
    - dbs (DBs): The database object containing pre-defined prompts and instructions.

    Returns:
    - str: The constructed system prompt for the AI.
    """
    return (
        dbs.preprompts["roadmap"]
        + dbs.preprompts["generate"].replace("FILE_FORMAT", dbs.preprompts["file_format"])
        + "\nUseful to know:\n"
        + dbs.preprompts["philosophy"]
    )


def setup_sys_prompt_existing_code(dbs: FileRepositories) -> str:
    """
    Constructs a system prompt for the AI focused on improving an existing codebase.

    This function sets up the system prompts for the AI, guiding it on how to
    work with and improve an existing code base. The generated prompt consists
    of the "improve" instruction (with dynamic format replacements) and the coding
    "philosophy" taken from the given DBs object.

    Parameters:
    - dbs (DBs): The database object containing pre-defined prompts and instructions.

    Returns:
    - str: The constructed system prompt focused on existing code improvement for the AI.
    """
    return (
        dbs.preprompts["improve"].replace("FILE_FORMAT", dbs.preprompts["file_format"])
        + "\nUseful to know:\n"
        + dbs.preprompts["philosophy"]
    )


def curr_fn() -> str:
    """
    Retrieves the name of the calling function.

    This function uses Python's inspection capabilities to dynamically fetch the
    name of the function that called `curr_fn()`. This approach ensures that the
    function's name isn't hardcoded, making it more resilient to refactoring and
    changes to function names.

    Returns:
    - str: The name of the function that called `curr_fn()`.
    """
    return inspect.stack()[1].function


def lite_gen(ai: AI, dbs: FileRepositories) -> List[Message]:
    """
    Executes the AI model using the main prompt and saves the generated results.

    This function invokes the AI model by feeding it the main prompt. After the
    AI processes and generates the output, the function saves this output to the
    specified workspace. The AI's output is also tracked using the current function's
    name to provide context.

    Parameters:
    - ai (AI): An instance of the AI model.
    - dbs (DBs): An instance containing the database configurations, including input prompts
      and file formatting preferences.

    Returns:
    - List[Message]: A list of message objects encapsulating the AI's output.

    Note:
    The function assumes the `ai.start` method and the `to_files` utility to be correctly
    set up and functional. Ensure these prerequisites before invoking `lite_gen`.
    """
    messages = ai.start(
        dbs.input["prompt"], dbs.preprompts["file_format"], step_name=curr_fn()
    )
    to_files_and_memory(messages[-1].content.strip(), dbs)
    return messages


def simple_gen(ai: AI, dbs: FileRepositories) -> List[Message]:
    """
    Executes the AI model using the default system prompts and saves the output.

    This function prepares the system prompt using the provided database configurations
    and then invokes the AI model with this system prompt and the main input prompt.
    Once the AI generates the output, this function saves it to the specified workspace.
    The AI's execution is tracked using the name of the current function for contextual reference.

    Parameters:
    - ai (AI): An instance of the AI model.
    - dbs (DBs): An instance containing the database configurations, including system and
      input prompts, and file formatting preferences.

    Returns:
    - List[Message]: A list of message objects encapsulating the AI's generated output.

    Note:
    The function assumes the `ai.start` method and the `to_files` utility are correctly
    set up and functional. Ensure these prerequisites are in place before invoking `simple_gen`.
    """
    messages = ai.start(setup_sys_prompt(dbs), dbs.input["prompt"], step_name=curr_fn())
    to_files_and_memory(messages[-1].content.strip(), dbs)
    return messages


def clarify(ai: AI, dbs: FileRepositories) -> List[Message]:
    """
    Interactively queries the user for clarifications on the prompt and saves the AI's responses.

    This function presents a series of clarifying questions to the user, based on the AI's
    initial assessment of the provided prompt. The user can continue to interact and seek
    clarifications until they indicate that they have "nothing to clarify" or manually
    opt to move on. If the user doesn't provide any input, the AI is instructed to make its
    own assumptions and to state them explicitly before proceeding.

    Parameters:
    - ai (AI): An instance of the AI model.
    - dbs (DBs): An instance containing the database configurations, which includes system
      and input prompts.

    Returns:
    - List[Message]: A list of message objects encapsulating the AI's generated output and
      interactions.

    """
    messages: List[Message] = [SystemMessage(content=dbs.preprompts["clarify"])]
    user_input = dbs.input["prompt"]
    while True:
        messages = ai.next(messages, user_input, step_name=curr_fn())
        msg = messages[-1].content.strip()

        if "nothing to clarify" in msg.lower():
            break

        if msg.lower().startswith("no"):
            print("Nothing to clarify.")
            break

        print()
        user_input = input('(answer in text, or "c" to move on)\n')
        print()

        if not user_input or user_input == "c":
            print("(letting gpt-engineer make its own assumptions)")
            print()
            messages = ai.next(
                messages,
                "Make your own assumptions and state them explicitly before starting",
                step_name=curr_fn(),
            )
            print()
            return messages

        user_input += """
            \n\n
            Is anything else unclear? If yes, ask another question.\n
            Otherwise state: "Nothing to clarify"
            """

    print()
    return messages


def gen_clarified_code(ai: AI, dbs: FileRepositories) -> List[dict]:
    """
    Generates code based on clarifications obtained from the user.

    This function processes the messages logged during the user's clarification session
    and uses them, along with the system's prompts, to guide the AI in generating code.
    The generated code is saved to a specified workspace.

    Parameters:
    - ai (AI): An instance of the AI model, responsible for processing and generating the code.
    - dbs (DBs): An instance containing the database configurations, which includes system
      and input prompts.

    Returns:
    - List[dict]: A list of message dictionaries capturing the AI's interactions and generated
      outputs during the code generation process.
    """
    messages = AI.deserialize_messages(dbs.logs[clarify.__name__])

    messages = [
        SystemMessage(content=setup_sys_prompt(dbs)),
    ] + messages[
        1:
    ]  # skip the first clarify message, which was the original clarify priming prompt
    messages = ai.next(
        messages,
        dbs.preprompts["generate"].replace("FILE_FORMAT", dbs.preprompts["file_format"]),
        step_name=curr_fn(),
    )

    to_files_and_memory(messages[-1].content.strip(), dbs)
    return messages


def execute_entrypoint(ai: AI, dbs: FileRepositories) -> List[dict]:
    """
    Executes the specified entry point script (`run.sh`) from a workspace.

    This function prompts the user to confirm whether they wish to execute a script named
    'run.sh' located in the specified workspace. If the user confirms, the script is
    executed using a subprocess. The user is informed that they can interrupt the
    execution at any time using ctrl+c.

    Parameters:
    - ai (AI): An instance of the AI model, not directly used in this function but
      included for consistency with other functions.
    - dbs (DBs): An instance containing the database configurations and workspace
      information.

    Returns:
    - List[dict]: An empty list. This function does not produce a list of messages
      but returns an empty list for consistency with the return type of other related
      functions.

    Note:
    The function assumes the presence of a 'run.sh' script in the specified workspace.
    Ensure the script is available and that it has the appropriate permissions
    (e.g., executable) before invoking this function.
    """
    command = dbs.workspace["run.sh"]

    print()
    print(
        colored(
            "Do you want to execute this code? (Y/n)",
            "red",
        )
    )
    print()
    print(command)
    print()
    if input().lower() not in ["", "y", "yes"]:
        print("Ok, not executing the code.")
        return []
    print("Executing the code...")
    print()
    print(
        colored(
            "Note: If it does not work as expected, consider running the code"
            + " in another way than above.",
            "green",
        )
    )
    print()
    print("You can press ctrl+c *once* to stop the execution.")
    print()

    p = subprocess.Popen("bash run.sh", shell=True, cwd=dbs.workspace.path)
    try:
        p.wait()
    except KeyboardInterrupt:
        print()
        print("Stopping execution.")
        print("Execution stopped.")
        p.kill()
        print()

    return []


def gen_entrypoint(ai: AI, dbs: FileRepositories) -> List[dict]:
    """
    Generates an entry point script based on a given codebase's information.

    This function prompts the AI model to generate a series of Unix terminal commands
    required to a) install dependencies and b) run all necessary components of a codebase
    provided in the workspace. The generated commands are then saved to 'run.sh' in the
    workspace.

    Parameters:
    - ai (AI): An instance of the AI model.
    - dbs (DBs): An instance containing the database configurations and workspace
      information, particularly the 'all_output.txt' which contains details about the
      codebase on disk.

    Returns:
    - List[dict]: A list of messages containing the AI's response.

    Notes:
    - The AI is instructed not to install packages globally, use 'sudo', provide
      explanatory comments, or use placeholders. Instead, it should use example values
      where necessary.
    - The function uses regular expressions to extract command blocks from the AI's
      response to create the 'run.sh' script.
    - It assumes the presence of an 'all_output.txt' file in the specified workspace
      that contains information about the codebase.
    """
    messages = ai.start(
        system=(
            "You will get information about a codebase that is currently on disk in "
            "the current folder.\n"
            "From this you will answer with code blocks that includes all the necessary "
            "unix terminal commands to "
            "a) install dependencies "
            "b) run all necessary parts of the codebase (in parallel if necessary).\n"
            "Do not install globally. Do not use sudo.\n"
            "Do not explain the code, just give the commands.\n"
            "Do not use placeholders, use example values (like . for a folder argument) "
            "if necessary.\n"
        ),
        user="Information about the codebase:\n\n" + dbs.memory["all_output.txt"],
        step_name=curr_fn(),
    )
    print()

    regex = r"```\S*\n(.+?)```"
    matches = re.finditer(regex, messages[-1].content.strip(), re.DOTALL)
    dbs.workspace["run.sh"] = "\n".join(match.group(1) for match in matches)
    return messages


def use_feedback(ai: AI, dbs: FileRepositories):
    """
    Uses the provided feedback to improve the generated code.

    This function takes in user feedback and applies it to modify previously
    generated code. If feedback is available, the AI model is primed with the
    system prompt and user instructions and then proceeds to process the feedback.
    The modified code is then saved back to the workspace. If feedback is not found,
    the user is informed to provide a 'feedback' file in the appropriate directory.

    Parameters:
    - ai (AI): An instance of the AI model.
    - dbs (DBs): An instance containing the database configurations and workspace
      information, particularly the 'all_output.txt' which contains the previously
      generated code, and 'input' which may contain the feedback from the user.

    Notes:
    - The function assumes the feedback will be found in 'dbs.input["feedback"]'.
    - If feedback is provided, the AI processes it and the resulting code is saved
      back to the workspace.
    - If feedback is absent, an instruction is printed to the console, and the program
      terminates.
    """
    messages = [
        SystemMessage(content=setup_sys_prompt(dbs)),
        HumanMessage(content=f"Instructions: {dbs.input['prompt']}"),
        AIMessage(
            content=dbs.memory["all_output.txt"]
        ),  # reload previously generated code
    ]
    if dbs.input["feedback"]:
        messages = ai.next(messages, dbs.input["feedback"], step_name=curr_fn())
        to_files_and_memory(messages[-1].content.strip(), dbs)
        return messages
    else:
        print(
            "No feedback was found in the input folder. Please create a file "
            + "called 'feedback' in the same folder as the prompt file."
        )
        exit(1)


def set_improve_filelist(ai: AI, dbs: FileRepositories):
    """
    Set the list of files for the AI to work with in the 'existing code mode'.

    This function initiates the process to determine which files from an existing
    codebase the AI should work with. By calling `ask_for_files()`, it prompts for
    and sets the specific files that should be considered, storing their full paths.

    Parameters:
    - ai (AI): An instance of the AI model. Although passed to this function, it is
      not used within the function scope and might be for consistency with other
      function signatures.
    - dbs (DBs): An instance containing the database configurations and project metadata,
      which is used to gather information about the existing codebase. Additionally,
      the 'input' is used to handle user interactions related to file selection.

    Returns:
    - list: Returns an empty list, which can be utilized for consistency in return
      types across related functions.

    Note:
    - The selected file paths are stored as a side-effect of calling `ask_for_files()`,
      and they aren't directly returned by this function.
    """
    """Sets the file list for files to work with in existing code mode."""
    ask_for_files(dbs.project_metadata, dbs.workspace)  # stores files as full paths.
    return []


def vector_improve(ai: AI, dbs: FileRepositories):
    code_vector_repository = CodeVectorRepository()
    code_vector_repository.load_from_directory(dbs.workspace.path)
    releventDocuments = code_vector_repository.relevent_code_chunks(dbs.input["prompt"])

    code_file_list = f"Here is a list of all the existing code files present in the root directory your code will be added to:"
    code_file_list += "\n {fileRepositories.workspace.to_path_list_string()}"

    relevent_file_contents = f"Here are files relevent to the query which you may like to change, reference or add to \n"

    for doc in releventDocuments:
        filename_without_path = Path(doc.metadata["filename"]).name
        file_content = dbs.workspace[filename_without_path]
        relevent_file_contents += format_file_to_input(
            filename_without_path, file_content
        )

    messages = [
        SystemMessage(content=setup_sys_prompt_existing_code(dbs)),
    ]

    messages.append(HumanMessage(content=f"{code_file_list}"))
    messages.append(HumanMessage(content=f"{relevent_file_contents}"))
    messages.append(HumanMessage(content=f"Request: {dbs.input['prompt']}"))

    messages = ai.next(messages, step_name=curr_fn())

    overwrite_files_with_edits(messages[-1].content.strip(), dbs)
    return messages


def assert_files_ready(ai: AI, dbs: FileRepositories):
    """
    Verify the presence of required files for headless 'improve code' execution.

    This function checks the existence of 'file_list.txt' in the project metadata
    and the presence of a 'prompt' in the input. If either of these checks fails,
    an assertion error is raised to alert the user of the missing requirements.

    Parameters:
    - ai (AI): An instance of the AI model. Although passed to this function, it is
      not used within the function scope and might be for consistency with other
      function signatures.
    - dbs (DBs): An instance containing the database configurations and project metadata,
      which is used to validate the required files' presence.

    Returns:
    - list: Returns an empty list, which can be utilized for consistency in return
      types across related functions.

    Raises:
    - AssertionError: If 'file_list.txt' is not present in the project metadata
      or if 'prompt' is not present in the input.

    Notes:
    - This function is typically used in 'auto_mode' scenarios to ensure that the
      necessary files are set up correctly before proceeding with the 'improve code'
      operation.
    """
    """Checks that the required files are present for headless
    improve code execution."""
    assert (
        "file_list.txt" in dbs.project_metadata
    ), "For auto_mode file_list.txt need to be in your .gpteng folder."
    assert "prompt" in dbs.input, "For auto_mode a prompt file must exist."
    return []


def get_improve_prompt(ai: AI, dbs: FileRepositories):
    """
    Asks the user what they would like to fix.
    """

    if not dbs.input.get("prompt"):
        dbs.input["prompt"] = input(
            "\nWhat do you need to improve with the selected files?\n"
        )

    confirm_str = "\n".join(
        [
            "-----------------------------",
            "The following files will be used in the improvement process:",
            f"{FILE_LIST_NAME}:",
            colored(str(dbs.project_metadata[FILE_LIST_NAME]), "green"),
            "",
            "The inserted prompt is the following:",
            colored(f"{dbs.input['prompt']}", "green"),
            "-----------------------------",
            "",
            "You can change these files in your project before proceeding.",
            "",
            "Press enter to proceed with modifications.",
            "",
        ]
    )
    input(confirm_str)
    return []


def improve_existing_code(ai: AI, dbs: FileRepositories):
    """
    Process and improve the code from a specified set of existing files based on a user prompt.

    This function first retrieves the code from the designated files and then formats this
    code to be processed by the Language Learning Model (LLM). After setting up the system prompt
    for existing code improvements, the files' contents are sent to the LLM. Finally, the user's
    prompt detailing desired improvements is passed to the LLM, and the subsequent response
    from the LLM is used to overwrite the original files.

    Parameters:
    - ai (AI): An instance of the AI model that is responsible for processing and generating
      responses based on the provided system and user inputs.
    - dbs (DBs): An instance containing the database configurations, user prompts, and project metadata.
      It is used to fetch the selected files for improvement and the user's improvement prompt.

    Returns:
    - list[Message]: Returns a list of Message objects that record the interaction between the
      system, user, and the AI model. This includes both the input to and the response from the LLM.

    Notes:
    - Ensure that the user has correctly set up the desired files for improvement and provided an
      appropriate prompt before calling this function.
    - The function expects the files to be formatted in a specific way to be properly processed by the LLM.
    """

    """
    After the file list and prompt have been aquired, this function is called
    to sent the formatted prompt to the LLM.
    """

    files_info = get_code_strings(
        dbs.workspace, dbs.project_metadata
    )  # this has file names relative to the workspace path

    messages = [
        SystemMessage(content=setup_sys_prompt_existing_code(dbs)),
    ]
    # Add files as input
    for file_name, file_str in files_info.items():
        code_input = format_file_to_input(file_name, file_str)
        messages.append(HumanMessage(content=f"{code_input}"))

    messages.append(HumanMessage(content=f"Request: {dbs.input['prompt']}"))

    messages = ai.next(messages, step_name=curr_fn())

    overwrite_files_with_edits(messages[-1].content.strip(), dbs)
    return messages


def human_review(ai: AI, dbs: FileRepositories):
    """
    Collects human feedback on the code and stores it in memory.

    This function prompts the user for a review of the generated or improved code using the `human_review_input`
    function. If a valid review is provided, it's serialized to JSON format and stored within the database's
    memory under the "review" key.

    Parameters:
    - ai (AI): An instance of the AI model. Although not directly used within the function, it is kept as
      a parameter for consistency with other functions.
    - dbs (DBs): An instance containing the database configurations, user prompts, project metadata,
      and memory storage. This function specifically interacts with the memory storage to save the human review.

    Returns:
    - list: Returns an empty list, indicating that there's no subsequent interaction with the LLM
      or no further messages to be processed.

    Notes:
    - It's assumed that the `human_review_input` function handles all the interactions with the user to
      gather feedback and returns either the feedback or None if no feedback was provided.
    - Ensure that the database's memory has enough space or is set up correctly to store the serialized review data.
    """

    """Collects and stores human review of the code"""
    review = human_review_input()
    if review is not None:
        dbs.memory["review"] = review.to_json()  # type: ignore
    return []


def self_heal(ai: AI, dbs: FileRepositories):
    """Attempts to execute the code from the entrypoint and if it fails,
    sends the error output back to the AI with instructions to fix.
    This code will make `MAX_SELF_HEAL_ATTEMPTS` to try and fix the code
    before giving up.
    This makes the assuption that the previous step was `gen_entrypoint`,
    this code could work with `simple_gen`, or `gen_clarified_code` as well.
    """

    # step 1. execute the entrypoint
    log_path = dbs.workspace.path / "log.txt"

    attempts = 0
    messages = []

    while attempts < MAX_SELF_HEAL_ATTEMPTS:
        log_file = open(log_path, "w")  # wipe clean on every iteration
        timed_out = False

        p = subprocess.Popen(  # attempt to run the entrypoint
            "bash run.sh",
            shell=True,
            cwd=dbs.workspace.path,
            stdout=log_file,
            stderr=log_file,
            bufsize=0,
        )
        try:  # timeout if the process actually runs
            p.wait(timeout=ASSUME_WORKING_TIMEOUT)
        except subprocess.TimeoutExpired:
            timed_out = True
            print("The process hit a timeout before exiting.")

        # get the result and output
        # step 2. if the return code not 0, package and send to the AI
        if p.returncode != 0 and not timed_out:
            print("run.sh failed.  Let's fix it.")

            # pack results in an AI prompt

            # Using the log from the previous step has all the code and
            # the gen_entrypoint prompt inside.
            if attempts < 1:
                messages = AI.deserialize_messages(dbs.logs[gen_entrypoint.__name__])
                messages.append(ai.fuser(get_platform_info()))  # add in OS and Py version

            # append the error message
            messages.append(ai.fuser(dbs.workspace["log.txt"]))

            messages = ai.next(
                messages, dbs.preprompts["file_format_fix"], step_name=curr_fn()
            )
        else:  # the process did not fail, we are done here.
            return messages

        log_file.close()

        # this overwrites the existing files
        to_files_and_memory(messages[-1].content.strip(), dbs)
        attempts += 1

    return messages


class Config(str, Enum):
    """
    Enumeration representing different configuration modes for the code processing system.

    Members:
    - DEFAULT: Standard procedure for generating, executing, and reviewing code.
    - BENCHMARK: Used for benchmarking the system's performance without execution.
    - SIMPLE: A basic procedure involving generation, execution, and review.
    - LITE: A lightweight procedure for generating code without further processing.
    - CLARIFY: Process that starts with clarifying ambiguities before code generation.
    - EXECUTE_ONLY: Only executes the code without generation.
    - EVALUATE: Execute the code and then undergo a human review.
    - USE_FEEDBACK: Uses prior feedback for code generation and subsequent steps.
    - IMPROVE_CODE: Focuses on improving existing code based on a provided prompt.
    - EVAL_IMPROVE_CODE: Validates files and improves existing code.
    - EVAL_NEW_CODE: Evaluates newly generated code without further steps.

    Each configuration mode dictates the sequence and type of operations performed on the code.
    """

    DEFAULT = "default"
    BENCHMARK = "benchmark"
    SIMPLE = "simple"
    LITE = "lite"
    CLARIFY = "clarify"
    EXECUTE_ONLY = "execute_only"
    EVALUATE = "evaluate"
    USE_FEEDBACK = "use_feedback"
    IMPROVE_CODE = "improve_code"
    EVAL_IMPROVE_CODE = "eval_improve_code"
    EVAL_NEW_CODE = "eval_new_code"
    VECTOR_IMPROVE = "vector_improve"
    SELF_HEAL = "self_heal"


STEPS = {
    Config.DEFAULT: [
        simple_gen,
        gen_entrypoint,
        execute_entrypoint,
        human_review,
    ],
    Config.LITE: [
        lite_gen,
    ],
    Config.CLARIFY: [
        clarify,
        gen_clarified_code,
        gen_entrypoint,
        execute_entrypoint,
        human_review,
    ],
    Config.BENCHMARK: [
        simple_gen,
        gen_entrypoint,
    ],
    Config.SIMPLE: [
        simple_gen,
        gen_entrypoint,
        execute_entrypoint,
    ],
    Config.USE_FEEDBACK: [use_feedback, gen_entrypoint, execute_entrypoint, human_review],
    Config.EXECUTE_ONLY: [execute_entrypoint],
    Config.EVALUATE: [execute_entrypoint, human_review],
    Config.IMPROVE_CODE: [
        set_improve_filelist,
        get_improve_prompt,
        improve_existing_code,
    ],
    Config.VECTOR_IMPROVE: [vector_improve],
    Config.EVAL_IMPROVE_CODE: [assert_files_ready, improve_existing_code],
    Config.EVAL_NEW_CODE: [simple_gen],
    Config.SELF_HEAL: [self_heal],
}
"""
A dictionary mapping Config modes to a list of associated processing steps.

The STEPS dictionary dictates the sequence of functions or operations to be
performed based on the selected configuration mode from the Config enumeration.
This enables a flexible system where the user can select the desired mode and
the system can execute the corresponding steps in sequence.

Examples:
- For Config.DEFAULT, the system will first generate the code using `simple_gen`,
  then generate the entry point with `gen_entrypoint`, execute the generated
  code using `execute_entrypoint`, and finally collect human review using `human_review`.
- For Config.LITE, the system will only use the `lite_gen` function to generate the code.

This setup allows for modularity and flexibility in handling different user requirements and scenarios.
"""

# Future steps that can be added:
# run_tests_and_fix_files
# execute_entrypoint_and_fix_files_if_it_results_in_error
