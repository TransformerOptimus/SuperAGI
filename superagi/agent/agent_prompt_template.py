import re

from pydantic.types import List

from superagi.helper.prompt_reader import PromptReader

FINISH_NAME = "finish"


class AgentPromptTemplate:

    @staticmethod
    def add_list_items_to_string(items: List[str]) -> str:
        list_string = ""
        for i, item in enumerate(items):
            list_string += f"{i + 1}. {item}\n"
        return list_string

    @classmethod
    def clean_prompt(cls, prompt):
        prompt = re.sub('[ \t]+', ' ', prompt)
        return prompt.strip()

    @classmethod
    def get_super_agi_single_prompt(cls):
        super_agi_prompt = PromptReader.read_agent_prompt(__file__, "superagi.txt")

        return {"prompt": super_agi_prompt, "variables": ["goals", "instructions", "constraints", "tools"]}

    @classmethod
    def start_task_based(cls):
        super_agi_prompt = PromptReader.read_agent_prompt(__file__, "initialize_tasks.txt")

        return {"prompt": AgentPromptTemplate.clean_prompt(super_agi_prompt), "variables": ["goals", "instructions"]}
        # super_agi_prompt = super_agi_prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(goals))

    @classmethod
    def analyse_task(cls):
        constraints = [
            'Exclusively use the tools listed in double quotes e.g. "tool name"'
        ]
        super_agi_prompt = PromptReader.read_agent_prompt(__file__, "analyse_task.txt")
        super_agi_prompt = AgentPromptTemplate.clean_prompt(super_agi_prompt) \
            .replace("{constraints}", AgentPromptTemplate.add_list_items_to_string(constraints))
        return {"prompt": super_agi_prompt, "variables": ["goals", "instructions", "tools", "current_task"]}

    @classmethod
    def create_tasks(cls):
        # just executed task `{last_task}` and got the result `{last_task_result}`
        super_agi_prompt = PromptReader.read_agent_prompt(__file__, "create_tasks.txt")
        return {"prompt": AgentPromptTemplate.clean_prompt(super_agi_prompt),
                "variables": ["goals", "instructions", "last_task", "last_task_result", "pending_tasks"]}

    @classmethod
    def prioritize_tasks(cls):
        # just executed task `{last_task}` and got the result `{last_task_result}`
        super_agi_prompt = PromptReader.read_agent_prompt(__file__, "prioritize_tasks.txt")
        return {"prompt": AgentPromptTemplate.clean_prompt(super_agi_prompt),
                "variables": ["goals", "instructions", "last_task", "last_task_result", "pending_tasks"]}
