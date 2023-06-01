import json
from pydantic.types import List
from superagi.agent.agent_prompt import AgentPrompt
from superagi.helper.token_counter import TokenCounter
from superagi.tools.base_tool import BaseTool
from fastapi_sqlalchemy import db
import re

FINISH_NAME = "finish"


class AgentPromptBuilder:

    @staticmethod
    def add_list_items_to_string(items: List[str]) -> str:
        list_string = ""
        for i, item in enumerate(items):
            list_string += f"{i + 1}. {item}\n"
        return list_string


    @classmethod
    def add_tools_to_prompt(cls, tools: List[BaseTool]):
        final_string = ""
        for i, item in enumerate(tools):
            final_string += f"{i + 1}. {cls._generate_command_string(item)}\n"
        finish_description = (
            "use this to signal that you have finished all your objectives"
        )
        finish_args = (
            '"response": "final response to let '
            'people know you have finished your objectives"'
        )
        finish_string = (
            f"{len(tools) + 1}. {FINISH_NAME}: "
            f"{finish_description}, args: {finish_args}"
        )
        final_string = final_string + finish_string + "\n\n"
        return final_string

    @classmethod
    def _generate_command_string(cls, tool: BaseTool) -> str:
        output = f"{tool.name}: {tool.description}"
        # print(tool.args)
        output += f", args json schema: {json.dumps(tool.args)}"
        return output
    @classmethod
    def clean_prompt(cls, prompt):
        prompt = re.sub(' +', ' ', prompt)
        return prompt

    @classmethod
    def get_super_agi_single_prompt(cls):
        response_format = {
            "thoughts": {
                "text": "thought",
                "reasoning": "reasoning",
                "plan": "- short bulleted\n- list that conveys\n- long-term plan",
                "criticism": "constructive self-criticism",
                "speak": "thoughts summary to say to user",
            },
            "tool": {"name": "tool name/task name", "description": "tool or task description",
                     "args": {"arg name": "value"}},
        }
        formatted_response_format = json.dumps(response_format, indent=4)

        super_agi_prompt = """You are SuperAGI an AI assistant to solve complex problems. Your decisions must always be made independently without seeking user assistance.
          Play to your strengths as an LLM and pursue simple strategies with no legal complications.
          If you have completed all your tasks or reached end state, make sure to use the "finish" tool.
    
          GOALS:
          {goals}
    
          CONSTRAINTS:
          {constraints}
          
          TOOLS:
          {tools}
          
          PERFORMANCE EVALUATION:
          1. Continuously review and analyze your actions to ensure you are performing to the best of your abilities. 
          2. Constructively self-criticize your big-picture behavior constantly.
          3. Reflect on past decisions and strategies to refine your approach.
          4. Every tool has a cost, so be smart and efficient.
          5. Aim to complete tasks in the least number of steps.
          
          I should only respond in JSON format as described below. 
          Response Format:
          {response_format}
          
          Ensure the response can be parsed by Python json.loads.
        """

        super_agi_prompt = AgentPromptBuilder.clean_prompt(super_agi_prompt).replace("{response_format}",
                                                                                     formatted_response_format)
        return {"prompt": super_agi_prompt, "variables": ["goals", "constraints", "tools"]}

    @classmethod
    def start_task_based(cls):
        super_agi_prompt = """You are a task-generating AI known as SuperAGI. You are not a part of any system or device. Your role is to understand the goals presented to you, identify important components, and construct a thorough execution plan.
        
        GOALS:
        {goals}
        
        Construct a sequence of actions, not exceeding 4 steps, to achieve this goal.
        
        Submit your response as a formatted ARRAY of strings, suitable for utilization with JSON.parse().
        
        Example: ["{{TASK-1}}", "{{TASK-2}}"].
        """

        return {"prompt": AgentPromptBuilder.clean_prompt(super_agi_prompt), "variables": ["goals"]}
        # super_agi_prompt = super_agi_prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(goals))

    # start task (push tasks) -> pop here -> analyse_task() -> command execute() -> create task()
    # what is each step doing?
    # execute the prompt with required variables.
    # analyze_task -> command execute() -> add to queue (get next best command)
    @classmethod
    def analyse_task(cls):
        constraints = [
            'Exclusively use the tools listed in double quotes e.g. "tool name"'
        ]
        super_agi_prompt = """
        High level goal: 
        {goals}
        
        Your Current Task: `{current_task}`
        
        Task History:
        `{task_history}`
        
        Based on this, your job is to understand the current task, pick out key parts, and think smart and fast. 
        Explain why you are doing each action, create a plan, and mention any worries you might have. 
        You have to pick your next action only from this list:
        
        TOOLS:
        {tools}
        
        CONSTRAINTS:
        {constraints}
        
        RESPONSE FORMAT:
        {
            "thoughts": {
                "reasoning": "reasoning"
            },
            "tool": {"name": "tool name", "args": {"arg name": "value"}},
        }
        
        Your answer must be something that JSON.parse() can read, and nothing else.
        """

        super_agi_prompt = AgentPromptBuilder.clean_prompt(super_agi_prompt) \
            .replace("{constraints}", AgentPromptBuilder.add_list_items_to_string(constraints))
        return {"prompt": super_agi_prompt, "variables": ["goals", "tools", "current_task"]}

    @classmethod
    def create_tasks(cls):
        # just executed task `{last_task}` and got the result `{last_task_result}`
        super_agi_prompt = """
        You are an AI assistant to create tasks.
        
        You are following objectives:
        {goals}
        
        You have following incomplete tasks `{pending_tasks}`. You have following completed tasks `{completed_tasks}`.
        
        Task History of completed tasks:
        `{task_history}`
         
        Based on this, create a new task for your AI system ONLY IF REQUIRED to get closer to or fully reach your goal.
        New tasks should be different from incomplete or completed tasks. 
        Your answer should be an array of strings that can be used with JSON.parse() and NOTHING ELSE. Return empty array if no new tasks are required.
        """
        return {"prompt": AgentPromptBuilder.clean_prompt(super_agi_prompt),
                "variables": ["goals", "last_task", "last_task_result", "pending_tasks"]}

    @classmethod
    def replace_main_variables(cls, super_agi_prompt: str, goals: List[str], constraints: List[str],
                               tools: List[BaseTool]):
        super_agi_prompt = super_agi_prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(goals))
        super_agi_prompt = super_agi_prompt.replace("{constraints}",
                                                    AgentPromptBuilder.add_list_items_to_string(constraints))
        tools_string = AgentPromptBuilder.add_tools_to_prompt(tools)
        super_agi_prompt = super_agi_prompt.replace("{tools}", tools_string)
        return super_agi_prompt

    @classmethod
    def replace_task_based_variables(cls, super_agi_prompt: str, current_task: str, last_task: str,
                                     last_task_result: str, pending_tasks: List[str], completed_tasks: list, token_limit: int):
        if "{current_task}" in super_agi_prompt:
            super_agi_prompt = super_agi_prompt.replace("{current_task}", current_task)
        if "{last_task}" in super_agi_prompt:
            super_agi_prompt = super_agi_prompt.replace("{last_task}", last_task)
        if "{last_task_result}" in super_agi_prompt:
            super_agi_prompt = super_agi_prompt.replace("{last_task_result}", last_task_result)
        if "{pending_tasks}" in super_agi_prompt:
            super_agi_prompt = super_agi_prompt.replace("{pending_tasks}", str(pending_tasks))

        if "{completed_tasks}" in super_agi_prompt:
            completed_tasks_arr = []
            for task in reversed(completed_tasks):
                completed_tasks_arr.append(task['task'])
            super_agi_prompt = super_agi_prompt.replace("{completed_tasks}", str(completed_tasks_arr))

        base_token_limit = TokenCounter.count_message_tokens([{"role": "user", "content": super_agi_prompt}])
        pending_tokens = token_limit - base_token_limit
        final_output = ""
        if "{task_history}" in super_agi_prompt:
            for task in reversed(completed_tasks):
                final_output = f"Task: {task['task']}\nResult: {task['response']}\n" + final_output
                token_count = TokenCounter.count_message_tokens([{"role": "user", "content": final_output}])
                # giving buffer of 100 tokens
                if token_count > pending_tokens - 100:
                    break
            super_agi_prompt = super_agi_prompt.replace("{task_history}", "\n" + final_output + "\n")
        return super_agi_prompt
