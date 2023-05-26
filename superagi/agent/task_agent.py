import json
import time
from typing import List, Dict

import openai
from pydantic import ValidationError

from superagi.agent.agent_prompt_builder import AgentPromptBuilder
from superagi.agent.output_parser import BaseOutputParser
from superagi.agent.super_agi import FINISH
from superagi.helper.token_counter import TokenCounter
from superagi.llms.base_llm import BaseLlm
from superagi.tools.base_tool import BaseTool
from superagi.types.common import BaseMessage
from superagi.vector_store.base import VectorStore


class TaskAgent:
    def __init__(self,
                 ai_name: str,
                 ai_role: str,
                 llm: BaseLlm,
                 memory: VectorStore,
                 output_parser: BaseOutputParser,
                 tools: List[BaseTool],
                 goals: List[str],
                 ):
        self.ai_name = ai_name
        self.ai_role = ai_role
        self.full_message_history: List[BaseMessage] = []
        self.llm = llm
        self.memory = memory
        self.output_parser = output_parser
        self.tools = tools
        self.goals = goals
        self.tasks_list = [] #{'name': 'GoogleSearch', 'id': '1', 'speak': 'I will search for strategies on how to win the World Cup.', 'reasoning': 'To gather information on winning strategies for the World Cup.', 'args': {'query': 'how to win the world cup'}}]
        self.last_executed_task_id = ""
        self.task_responses = {}
        self.tasks_stack = []
        self.incomplete_tasks = [] #{'name': 'GoogleSearch', 'id': '1', 'speak': 'I will search for strategies on how to win the World Cup.', 'reasoning': 'To gather information on winning strategies for the World Cup.', 'args': {'query': 'how to win the world cup'}}]

    def create_task(self, goals_override: str = None):
        user_input = (
            "Determine the next set of tasks to execute and respond using the format specified above."
        )

        if self.last_executed_task_id not in self.task_responses:
            last_task_response = ""
            last_task_desc = ""
        else:
            #task_agent.task_responses[task_agent.last_executed_task_id]['response']
            last_task_response = str(self.task_responses[self.last_executed_task_id]['response'])
            last_task_desc = self.task_responses[self.last_executed_task_id]["name"] + ":" + self.task_responses[self.last_executed_task_id]["description"]
            # goals changed

        goals = self.goals
        if goals_override is not None:
            goals = goals_override
            last_task_response = ""
            last_task_desc = ""

        completed_tasks = []
        for task in self.tasks_list:
            if task['id'] in self.task_responses:
                completed_tasks.append(task)

        babyagi_prompt = AgentPromptBuilder.get_babyagi_prompt(self.ai_name, self.ai_role, goals, self.tools, self.completed_tasks, self.incomplete_tasks, last_task_desc, last_task_response)
        messages = [{"role": "system", "content": babyagi_prompt},
                    {"role": "system", "content": f"The current time and date is {time.strftime('%c')}"}]

        current_tokens = TokenCounter.count_message_tokens(messages, self.llm.get_model())
        token_limit = TokenCounter.token_limit(self.llm.get_model())
        response = self.llm.chat_completion(messages, token_limit - current_tokens)

        if response['content'] is None:
            raise RuntimeError(f"Failed to get response from llm")
        assistant_reply = response['content']

        action = self.output_parser.parse_tasks(assistant_reply)
        for task in action.tasks:
            self.tasks_list.append(task)
            self.incomplete_tasks.append(task)
        print(self.tasks_list)
        return

    def execution_llm_agent(self, task: str) -> str:
        goals_list = ','.join(self.goals)
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"You are an AI who performs one task based on the following goals: {goals_list}. Your task: {task}\nResponse:",
            temperature=0.7,
            max_tokens=2000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].text.strip()

    def execute_task(self):
        if len(self.tasks_list) == 0:
            return
        task = self.incomplete_tasks[0]
        self.tasks_stack.append(task)
        tools = {t.name: t for t in self.tools}
        if task["id"] not in self.task_responses:
            self.task_responses[task["id"]] = {}
        if task["name"] == FINISH:
            self.task_responses[task["id"]]['name'] = task["name"]
            self.task_responses[task["id"]]['description'] = task["description"]
            self.task_responses[task["id"]]['status'] = "COMPLETE"
            self.task_responses[task["id"]]['response'] = "FINSHED"
            return "Task finished"
        elif task["name"] in tools:
            tool = tools[task["name"]]
            try:
                observation = tool.execute(task["args"])
            except ValidationError as e:
                observation = (
                    f"Validation Error in args: {str(e)}, args: {task['args']}"
                )
            except Exception as e:
                observation = (
                    f"Error1: {str(e)}, {type(e).__name__}, args: {task['args']}"
                )
            self.task_responses[task["id"]]['name'] = task["name"]
            self.task_responses[task["id"]]['description'] = task["description"]
            self.task_responses[task["id"]]['response'] = observation
            self.task_responses[task["id"]]['status'] = "COMPLETE"
        else:
            response = self.execution_llm_agent(task["description"])
            # free will task
            self.task_responses[task["id"]]['name'] = task["name"]
            self.task_responses[task["id"]]['description'] = task["description"]
            self.task_responses[task["id"]]['status'] = "COMPLETE"
            self.task_responses[task["id"]]['response'] = response

            #result = f"Tool {tool.name} returned: {observation}"
        updated_incomplete_tasks = []
        for intask in self.incomplete_tasks:
            if task["id"] != intask['id']:
                updated_incomplete_tasks.append(intask)
        self.incomplete_tasks = updated_incomplete_tasks
        self.last_executed_task_id = task["id"]
        print(self.task_responses)
        return

    def add_list_items_to_string(self, title: str, items: List[str]) -> str:
        list_string = ""
        for i, item in enumerate(items):
            list_string += f"{i + 1}. {item}\n"
        if list_string == "":
            return ""
        return title + ":\n" + list_string + "\n"

    def prioritize_task(self):
        prompt = "You are an task prioritization AI tasked with cleaning the formatting of and reprioritizing the following tasks in json format: \n"
        prompt = prompt + self.add_list_items_to_string("\nINCOMPLETE TASKS:\n", self.incomplete_tasks)

        prompt += ". Consider the ultimate goal of your team. Do not remove any tasks. Return the result as a json list in the same format as input."
        prompt = prompt + self.add_list_items_to_string("\nGOALS:", self.goals)

        response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, temperature=0.5, max_tokens=1000,
                                            top_p=1, frequency_penalty=0, presence_penalty=0)
        new_tasks = response.choices[0].text.strip().split('\n')
        print(new_tasks)
        task_list = []
        for task_string in new_tasks:
            task_parts = task_string.strip().split(".", 1)
            if len(task_parts) == 2:
                # task_id = task_parts[0].strip()
                task_json = json.loads(task_parts[1].strip())
                task_list.append({"name": task_json["name"], "description": task_json["description"], "id": task_json["id"], "args": task_json["args"]})

        if task_list is not None:
            self.incomplete_tasks = task_list
        return

