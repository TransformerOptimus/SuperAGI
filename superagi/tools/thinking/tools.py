from typing import Type, Optional, List

from pydantic import BaseModel, Field

from superagi.agent.agent_prompt_builder import AgentPromptBuilder
from superagi.helper.error_handler import ErrorHandler
from superagi.helper.prompt_reader import PromptReader
from superagi.lib.logger import logger
from superagi.llms.base_llm import BaseLlm
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_execution_feed import AgentExecutionFeed
from superagi.tools.base_tool import BaseTool
from superagi.tools.tool_response_query_manager import ToolResponseQueryManager


class ThinkingSchema(BaseModel):
    task_description: str = Field(
        ...,
        description="Task description which needs reasoning.",
    )

class ThinkingTool(BaseTool):
    """
    Thinking tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
        llm: LLM used for thinking.
    """
    llm: Optional[BaseLlm] = None
    name = "ThinkingTool"
    description = (
        "Intelligent problem-solving assistant that comprehends tasks, identifies key variables, and makes efficient decisions, all while providing detailed, self-driven reasoning for its choices. Do not assume anything, take the details from given data only."
    )
    args_schema: Type[ThinkingSchema] = ThinkingSchema
    goals: List[str] = []
    agent_execution_id:int=None
    agent_id:int = None
    permission_required: bool = False
    tool_response_manager: Optional[ToolResponseQueryManager] = None

    class Config:
        arbitrary_types_allowed = True


    def _execute(self, task_description: str):
        """
        Execute the Thinking tool.

        Args:
            task_description : The task description.

        Returns:
            Thought process of llm for the task
        """
        try:
            prompt = PromptReader.read_tools_prompt(__file__, "thinking.txt")
            prompt = prompt.replace("{goals}", AgentPromptBuilder.add_list_items_to_string(self.goals))
            prompt = prompt.replace("{task_description}", task_description)
            last_tool_response = self.tool_response_manager.get_last_response()
            prompt = prompt.replace("{last_tool_response}", last_tool_response)
            metadata = {"agent_execution_id":self.agent_execution_id}
            relevant_tool_response = self.tool_response_manager.get_relevant_response(query=task_description,metadata=metadata)
            prompt = prompt.replace("{relevant_tool_response}",relevant_tool_response)
            messages = [{"role": "system", "content": prompt}]
            result = self.llm.chat_completion(messages, max_tokens=self.max_token_limit)
            
            if 'error' in result and result['message'] is not None:
                ErrorHandler.handle_openai_errors(self.toolkit_config.session, self.agent_id, self.agent_execution_id, result['message'])
            return result["content"]
        except Exception as e:
            logger.error(e)
            return f"Error generating text: {e}"