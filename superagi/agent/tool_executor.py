from pydantic import ValidationError

from superagi.agent.common_types import ToolExecutorResponse
from superagi.apm.event_handler import EventHandler
from superagi.lib.logger import logger


class ToolExecutor:
    """Executes the tool with the given args."""
    FINISH = "finish"

    def __init__(self, organisation_id: int, agent_id: int, tools: list):
        self.organisation_id = organisation_id
        self.agent_id = agent_id
        self.tools = tools

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
            EventHandler(session=session).create_event('tool_used', {'tool_name': tool_name}, self.agent_id,
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
