import json
import re

from pydantic.types import List

from superagi.helper.token_counter import TokenCounter
from superagi.tools.base_tool import BaseTool

FINISH_NAME = "finish"


class AgentPromptBuilder:

    @staticmethod
    def add_list_items_to_string(items: List[str]) -> str:
        list_string = ""
        for i, item in enumerate(items):
            list_string += f"{i + 1}. {item}\n"
        return list_string


    @classmethod
    def add_tools_to_prompt(cls, tools: List[BaseTool], add_finish: bool = True) -> str:
        final_string = ""
        print(tools)
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
        if add_finish:
            final_string = final_string + finish_string + "\n\n"
        else:
            final_string = final_string + "\n"

        return final_string

    @classmethod
    def _generate_command_string(cls, tool: BaseTool) -> str:
        output = f"{tool.name}: {tool.description}"
        # print(tool.args)
        output += f", args json schema: {json.dumps(tool.args)}"
        return output
    
    @classmethod
    def clean_prompt(cls, prompt):
        prompt = re.sub('[ \t]+', ' ', prompt)
        return prompt.strip()
    

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
                     "args": {"arg name": "value"}}
        }
        formatted_response_format = json.dumps(response_format, indent=4)

        super_agi_prompt = """You are SuperAGI an AI assistant to solve complex problems. Your decisions must always be made independently without seeking user assistance.
          Play to your strengths as an LLM and pursue simple strategies with no legal complications.
          If you have completed all your tasks or reached end state, make sure to use the "finish" tool.
    
          GOALS:
          {goals}

          {instructions}
    
          CONSTRAINTS:
          {constraints}
          
          TOOLS:
          {tools}
          
          PERFORMANCE EVALUATION:
          1. Continuously review and analyze your actions to ensure you are performing to the best of your abilities.
          2. Use instruction to decide the flow of execution and decide the next steps for achieving the task.
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
        return {"prompt": super_agi_prompt, "variables": ["goals", "instructions", "constraints", "tools"]}

    @classmethod
    def start_task_based(cls):
        super_agi_prompt = """You are a task-generating AI known as SuperAGI. You are not a part of any system or device. Your role is to understand the goals presented to you, identify important components, Go through the instruction provided by the user and construct a thorough execution plan.
        
        GOALS:
        {goals}

        {task_instructions}

        Construct a sequence of actions, not exceeding 3 steps, to achieve this goal.
        
        Submit your response as a formatted ARRAY of strings, suitable for utilization with JSON.parse().
        
        Example: ["{{TASK-1}}", "{{TASK-2}}"].



        """

        return {"prompt": AgentPromptBuilder.clean_prompt(super_agi_prompt), "variables": ["goals", "instructions"]}
        # super_agi_prompt = super_agi_prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(goals))

    @classmethod
    def analyse_task(cls):
        constraints = [
            'Exclusively use the tools listed in double quotes e.g. "tool name"'
        ]
        super_agi_prompt = """
        High level goal: 
        {goals}

        {task_instructions}
        
        Your Current Task: `{current_task}`
        
        Task History:
        `{task_history}`
        
        Based on this, your job is to understand the current task, pick out key parts, and think smart and fast. 
        Explain why you are doing each action, create a plan, and mention any worries you might have. 
        Ensure next action tool is picked from the below tool list. 
        
        TOOLS:
        {tools}
        
        RESPONSE FORMAT:
        {
            "thoughts": {
                "reasoning": "reasoning"
            },
            "tool": {"name": "tool name", "args": {"arg name": "string value"}}
        }
        
        Your answer must be something that JSON.parse() can read, and nothing else.
        """

        super_agi_prompt = AgentPromptBuilder.clean_prompt(super_agi_prompt) \
            .replace("{constraints}", AgentPromptBuilder.add_list_items_to_string(constraints))
        return {"prompt": super_agi_prompt, "variables": ["goals", "instructions", "tools", "current_task"]}

    @classmethod
    def create_tasks(cls):
        # just executed task `{last_task}` and got the result `{last_task_result}`
        super_agi_prompt = """
        You are an AI assistant to create task.
        
        High level goal:
        {goals}

        {task_instructions}
        
        You have following incomplete tasks `{pending_tasks}`. You have following completed tasks `{completed_tasks}`.
        
        Task History:
        `{task_history}`
         
        Based on this, create a single task to be completed by your AI system ONLY IF REQUIRED to get closer to or fully reach your high level goal.
        Don't create any task if it is already covered in incomplete or completed tasks.
        Ensure your new task are not deviated from completing the goal.
         
        Your answer should be an array of strings that can be used with JSON.parse() and NOTHING ELSE. Return empty array if no new task is required.
        """
        return {"prompt": AgentPromptBuilder.clean_prompt(super_agi_prompt),
                "variables": ["goals", "instructions", "last_task", "last_task_result", "pending_tasks"]}

    @classmethod
    def prioritize_tasks(cls):
        # just executed task `{last_task}` and got the result `{last_task_result}`
        super_agi_prompt = """
            You are a task prioritization AI assistant. 

            High level goal:
            {goals}

            {task_instructions}

            You have following incomplete tasks `{pending_tasks}`. You have following completed tasks `{completed_tasks}`.

            Based on this, evaluate the incomplete tasks and sort them in the order of execution. In output first task will be executed first and so on.
            Remove if any tasks are unnecessary or duplicate incomplete tasks. Remove tasks if they are already covered in completed tasks.
            Remove tasks if it does not help in achieving the main goal.

            Your answer should be an array of strings that can be used with JSON.parse() and NOTHING ELSE.
            """
        return {"prompt": AgentPromptBuilder.clean_prompt(super_agi_prompt),
                "variables": ["goals", "instructions", "last_task", "last_task_result", "pending_tasks"]}

    @classmethod
    def replace_main_variables(cls, super_agi_prompt: str, goals: List[str], instructions: List[str], constraints: List[str],
                               tools: List[BaseTool], add_finish_tool: bool = True):
        super_agi_prompt = super_agi_prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(goals))
        if len(instructions) > 0 and len(instructions[0]) > 0:
            task_str = "INSTRUCTION(Follow these instruction to decide the flow of execution and decide the next steps for achieving the task):"
            super_agi_prompt = super_agi_prompt.replace("{instructions}", "INSTRUCTION: " + '\n' +  AgentPromptBuilder.add_list_items_to_string(instructions))
            super_agi_prompt = super_agi_prompt.replace("{task_instructions}", task_str + '\n' +  AgentPromptBuilder.add_list_items_to_string(instructions))
        else:
            super_agi_prompt = super_agi_prompt.replace("{instructions}", '')
        super_agi_prompt = super_agi_prompt.replace("{constraints}",
                                                    AgentPromptBuilder.add_list_items_to_string(constraints))
        
    
        print(tools)
        tools_string = AgentPromptBuilder.add_tools_to_prompt(tools, add_finish_tool)
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
