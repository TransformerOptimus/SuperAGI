import re

from pydantic.types import List

from superagi.helper.prompt_reader import PromptReader
from superagi.lib.logger import logger
from superagi.models.agent import Agent

FINISH_NAME = "finish"


class ClusterPromptBuilder:

    @staticmethod
    def add_list_items_to_string(items: List[str]) -> str:
        list_string = ""
        for i, item in enumerate(items):
            list_string += f"{i + 1}. {item}\n"
        return list_string

    @classmethod
    def add_agents_to_prompt(cls, tools: List[Agent]) -> str:
        final_string = ""
        print(tools)
        for i, item in enumerate(tools):
            final_string += f"{i + 1}. {cls._generate_command_string(item)}\n"

        final_string = final_string + "\n"

        return final_string

    @classmethod
    def _generate_command_string(cls, agent: Agent) -> str:
        output = f"{agent.name}: {agent.description}"
        # print(tool.args)
        return output

    @classmethod
    def clean_prompt(cls, prompt):
        prompt = re.sub('[ \t]+', ' ', prompt)
        return prompt.strip()

    @classmethod
    def initialize_tasks_prompt(cls):
        super_agi_prompt = PromptReader.read_agent_prompt(
            __file__, "initialize_tasks.txt")

        return {"prompt": cls.clean_prompt(super_agi_prompt), "variables":
                ["goals", "instructions", "agents"]}

    @classmethod
    def decide_agent_prompt(cls):
        super_agi_prompt = PromptReader.read_agent_prompt(
            __file__, "decide_agent.txt")

        return {"prompt": cls.clean_prompt(super_agi_prompt), "variables":
                ["goals", "instructions", "current_task", "agents"]}

    @classmethod
    def replace_main_variables(
            cls,
            super_agi_cluster_prompt: str,
            goals: List[str],
            instructions: List[str],
            agents: List[Agent]):
        super_agi_cluster_prompt = super_agi_cluster_prompt.replace(
            "{goals}", cls.add_list_items_to_string(goals))
        if len(instructions) > 0 and len(instructions[0]) > 0:
            task_str = "INSTRUCTION(Follow these instruction to decide the flow of execution and decide the next " \
                       "steps for achieving the task):"
            super_agi_cluster_prompt = super_agi_cluster_prompt.replace(
                "{task_instructions}", task_str + '\n' + cls.add_list_items_to_string(instructions))
        else:
            super_agi_cluster_prompt = super_agi_cluster_prompt.replace(
                "{instructions}", '')

        logger.info(agents)
        agents_string = cls.add_agents_to_prompt(agents)
        super_agi_cluster_prompt = super_agi_cluster_prompt.replace(
            "{agents}", agents_string)
        return super_agi_cluster_prompt

    @classmethod
    def replace_task_based_variables(
            cls,
            super_agi_cluster_prompt: str,
            current_task: str):
        if "{current_task}" in super_agi_cluster_prompt:
            super_agi_cluster_prompt = super_agi_cluster_prompt.replace(
                "{current_task}", current_task)
        return super_agi_cluster_prompt
