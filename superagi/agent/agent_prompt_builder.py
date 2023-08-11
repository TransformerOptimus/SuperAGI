import json
import re

from pydantic.types import List

from superagi.helper.token_counter import TokenCounter
from superagi.tools.base_tool import BaseTool

FINISH_NAME = "finish"


class AgentPromptBuilder:
    """Agent prompt builder for LLM agent."""

    @staticmethod
    def add_list_items_to_string(items: List[str]) -> str:
        list_string = ""
        for i, item in enumerate(items):
            list_string += f"{i + 1}. {item}\n"
        return list_string


    @classmethod
    def add_tools_to_prompt(cls, tools: List[BaseTool], add_finish: bool = True) -> str:
        """Add tools to the prompt.

        Args:
            tools (List[BaseTool]): The list of tools.
            add_finish (bool): Whether to add finish tool or not.
        """
        final_string = ""
        print(tools)
        for i, item in enumerate(tools):
            final_string += f"{i + 1}. {cls._generate_tool_string(item)}\n"
        finish_description = (
            "use this to signal that you have finished all your objectives"
        )
        finish_args = (
            '"response": "final response to let '
            'people know you have finished your objectives"'
        )
        finish_string = (
            f"{len(tools) + 1}. \"{FINISH_NAME}\": "
            f"{finish_description}, args: {finish_args}"
        )
        if add_finish:
            final_string = final_string + finish_string + "\n\n"
        else:
            final_string = final_string + "\n"

        return final_string

    @classmethod
    def _generate_tool_string(cls, tool: BaseTool) -> str:
        output = f"\"{tool.name}\": {tool.description}"
        # print(tool.args)
        output += f", args json schema: {json.dumps(tool.args)}"
        return output
    
    @classmethod
    def clean_prompt(cls, prompt):
        prompt = re.sub('[ \t]+', ' ', prompt)
        return prompt.strip()

    @classmethod
    def replace_main_variables(cls, super_agi_prompt: str, goals: List[str], instructions: List[str], constraints: List[str],
                               tools: List[BaseTool], add_finish_tool: bool = True):
        """Replace the main variables in the super agi prompt.

        Args:
            super_agi_prompt (str): The super agi prompt.
            goals (List[str]): The list of goals.
            instructions (List[str]): The list of instructions.
            constraints (List[str]): The list of constraints.
            tools (List[BaseTool]): The list of tools.
            add_finish_tool (bool): Whether to add finish tool or not.
        """
        super_agi_prompt = super_agi_prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(goals))
        if len(instructions) > 0 and len(instructions[0]) > 0:
            task_str = "INSTRUCTION(Follow these instruction to decide the flow of execution and decide the next steps for achieving the task):"
            super_agi_prompt = super_agi_prompt.replace("{instructions}", "INSTRUCTION: " + '\n' +  AgentPromptBuilder.add_list_items_to_string(instructions))
            super_agi_prompt = super_agi_prompt.replace("{task_instructions}", task_str + '\n' +  AgentPromptBuilder.add_list_items_to_string(instructions))
        else:
            super_agi_prompt = super_agi_prompt.replace("{instructions}", '')
        super_agi_prompt = super_agi_prompt.replace("{task_instructions}", "")
        super_agi_prompt = super_agi_prompt.replace("{constraints}",
                                                    AgentPromptBuilder.add_list_items_to_string(constraints))


        # logger.info(tools)
        tools_string = AgentPromptBuilder.add_tools_to_prompt(tools, add_finish_tool)
        super_agi_prompt = super_agi_prompt.replace("{tools}", tools_string)
        return super_agi_prompt

    @classmethod
    def replace_task_based_variables(cls, super_agi_prompt: str, current_task: str, last_task: str,
                                     last_task_result: str, pending_tasks: List[str], completed_tasks: list, token_limit: int):
        """Replace the task based variables in the super agi prompt.

        Args:
            super_agi_prompt (str): The super agi prompt.
            current_task (str): The current task.
            last_task (str): The last task.
            last_task_result (str): The last task result.
            pending_tasks (List[str]): The list of pending tasks.
            completed_tasks (list): The list of completed tasks.
            token_limit (int): The token limit.
        """
        if "{current_task}" in super_agi_prompt:
            super_agi_prompt = super_agi_prompt.replace("{current_task}", current_task)
        if "{last_task}" in super_agi_prompt:
            super_agi_prompt = super_agi_prompt.replace("{last_task}", last_task)
        if "{last_task_result}" in super_agi_prompt:
            super_agi_prompt = super_agi_prompt.replace("{last_task_result}", last_task_result)
        if "{pending_tasks}" in super_agi_prompt:
            super_agi_prompt = super_agi_prompt.replace("{pending_tasks}", str(pending_tasks))

        completed_tasks.reverse()
        if "{completed_tasks}" in super_agi_prompt:
            completed_tasks_arr = []
            for task in completed_tasks:
                completed_tasks_arr.append(task['task'])
            super_agi_prompt = super_agi_prompt.replace("{completed_tasks}", str(completed_tasks_arr))

        base_token_limit = TokenCounter.count_message_tokens([{"role": "user", "content": super_agi_prompt}])
        pending_tokens = token_limit - base_token_limit
        final_output = ""
        if "{task_history}" in super_agi_prompt:
            for task in reversed(completed_tasks[-10:]):
                final_output = f"Task: {task['task']}\nResult: {task['response']}\n" + final_output
                token_count = TokenCounter.count_message_tokens([{"role": "user", "content": final_output}])
                # giving buffer of 100 tokens
                if token_count > min(600, pending_tokens):
                    break
            super_agi_prompt = super_agi_prompt.replace("{task_history}", "\n" + final_output + "\n")
        return super_agi_prompt
