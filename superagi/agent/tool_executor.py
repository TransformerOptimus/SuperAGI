import json
from pydantic import ValidationError

from superagi.agent.common_types import ToolExecutorResponse
from superagi.apm.event_handler import EventHandler
from superagi.lib.logger import logger


class ToolExecutor:
    """Executes the tool with the given args."""
    FINISH = "finish"

    def __init__(self, organisation_id: int, agent_id: int, tools: list, agent_execution_id: int):
        self.organisation_id = organisation_id
        self.agent_id = agent_id
        self.tools = tools
        self.agent_execution_id = agent_execution_id

    def execute(self, session, tool_name, tool_args):
        """Executes the tool with the given args.

        Args:
            session (Session): The database session.
            tool_name (str): The name of the tool to execute.
            tool_args (dict): The arguments to pass to the tool.
        """
        tools = {t.name.lower().replace(" ", ""): t for t in self.tools}
        tool_name = tool_name.lower().replace(" ", "")
        if tool_name == ToolExecutor.FINISH or tool_name == "":
            logger.info("\nTask Finished :) \n")
            return ToolExecutorResponse(status="COMPLETE", result="")
        if tool_name in tools.keys():
            status = "SUCCESS"
            tool = tools[tool_name]
            retry = False
            EventHandler(session=session).create_event('tool_used', {'tool_name': tool.name, 'agent_execution_id': self.agent_execution_id}, self.agent_id,
                                                       self.organisation_id),
            try:
                parsed_args = self.clean_tool_args(tool_args)
                observation = tool.execute(parsed_args)
            except ValidationError as e:
                status = "ERROR"
                retry = True
                observation = (
                    f"Validation Error in args: {str(e)}, args: {tool_args}"
                )
            except Exception as e:
                status = "ERROR"
                retry = True
                observation = (
                    f"Error1: {str(e)}, {type(e).__name__}, args: {tool_args}"
                )
            output = ToolExecutorResponse(status=status, result=f"Tool {tool.name} returned: {observation}",
                                          retry=retry)
        elif tool_name == "ERROR":
            output = ToolExecutorResponse(status="ERROR", result=f"Error Tool Name: {tool_args}. ", retry=False)
        else:
            result = (
                f"Unknown tool '{tool_name}'. "
                f"Please refer to the 'TOOLS' list for available "
                f"tools and only respond in the specified JSON format."
            )
            output = ToolExecutorResponse(status="ERROR", result=result, retry=True)

        logger.info("Tool Response : " + str(output) + "\n")
        return output

    def clean_tool_args(self, args):
        parsed_args = {}
        for key in args.keys():
            parsed_args[key] = args[key]
            if type(args[key]) is dict and "value" in args[key]:
                parsed_args[key] = args[key]["value"]
        return parsed_args

    def  _get_tool_executor_prompt(self, tool_name, task, tool_schema, valid_plans):
        prompt = ""
        with open('superagi/agent/prompts/tool_executor.txt', 'r') as f:
            prompt = f.read()
        prompt = prompt.replace('{tool_name}', tool_name)
        prompt = prompt.replace('{task}', task)
        prompt = prompt.replace('{tool_schema}', tool_schema)
        prompt = prompt.replace('{valid_plans}', valid_plans)
        return prompt

    def _tool_executor_step(self, msgs: list, task: str, tool_name: str, tool_input: str, tool_output: str, llm):
        content = f'''Task: {task}

        Input to `{tool_name}` tool:
        {tool_input}

        Output from `{tool_name}` tool:
        {tool_output}

        Is the above output enough to complete the task?
        '''
        query = {"role": "user", "content": content}
        logger.info(f"########    {query['role']}\n\n{query['content']}\n\n")
        new_msgs = msgs + [query]
        c = llm.chat_completion(messages=new_msgs)

        # Step 2: check if GPT wanted to call a function
        logger.debug("_________TOOL_EXECUTOR_RESPONSE________")
        if c['content']:
            content = c['content']
            msg = {"role": "assistant", "content": content}
            msgs.append(query)
            msgs.append(msg)
            logger.info(f"########    {msg['role']}\n\n{msg['content']}\n\n")
            return msgs
        else:
            raise Exception(c)
    
    def _tool_executor(self, task: str, tool_input: str, output_handler, session, llm):
        msgs = []
        tool_name = 'googleserp'
        tool_schema = """{'properties': {'query': {'description': 'verbose query for google search', 'title': 'Query', 'type': 'string'}}, 'required': ['query'], 'title': 'Input for `google_serp`', 'type': 'object'}"""
        valid_plans = str(['Try a different search query',
                        'Add relevant data from the given task in search query'])
        system_prompt = self._get_tool_executor_prompt(tool_name, task, tool_schema, valid_plans)
        msg = {"role": "system", "content": system_prompt}
        msgs = [msg]
        logger.info(f"########    {msg['role']}\n\n{msg['content']}\n\n")
        output = output_handler.handle(session, tool_input)
        
        msgs = self._tool_executor_step(msgs=msgs, task=task, tool_name=tool_name, tool_input=tool_input, tool_output=output, llm=llm)
        logger.debug("MESSGAESSS: ", msgs)
        r = json.loads(msgs[-1]['content'])
        while (r['reasoning']['judgement'] != "Task Completed"):
            print("__________ENTERING WHILE LOOP__________")
            input = r['action']['input']
            input_for_tool = {
                "tool": {
                "name": "googleserp",
                "args": {
                    "query": input['query']
                }
            }}
            output = output_handler.handle(session, json.dumps(input_for_tool))
            msgs = self._tool_executor_step(msgs=msgs, task=task, tool_name=tool_name, tool_input=json.dumps(input_for_tool), tool_output=output, llm=llm)
            r = json.loads(msgs[-1]['content'])
        return r['reasoning']['final_answer']