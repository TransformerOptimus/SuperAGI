import json
from typing import Type, Optional

from pydantic import BaseModel, Field

from superagi.helper.google_search import GoogleSearchWrap
from superagi.helper.token_counter import TokenCounter
from superagi.llms.base_llm import BaseLlm
from superagi.models.agent_execution_feed import AgentExecutionFeed
from superagi.tools.base_tool import BaseTool
from superagi.models.agent_execution_config import AgentExecutionConfiguration
from superagi.models.workflows.agent_workflow_step_tool import AgentWorkflowStepTool
from superagi.models.agent_execution import AgentExecution
from superagi.models.workflows.agent_workflow_step import AgentWorkflowStep


class WebInteractorStarterSchema(BaseModel):
    goal: str = Field(
        ...,
        description="goal of the current execution"
    )


class WebInteractorStarterTool(BaseTool):
    """
    Web Interactor Started tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """
    llm: Optional[BaseLlm] = None
    name = "WebInteractorStarter"
    agent_execution_id: int = None
    description = (
        "A tool for initialising the web interactor tool"
        # "Input should be a search query."
    )
    args_schema: Type[WebInteractorStarterSchema] = WebInteractorStarterSchema

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, goal: str):
        """
        Starts the Web Interactor tool.

        Args:
            goal : Starts the web interactor tool

        Returns:
            str
        """
        # print("************URL",curr_page_url)

        return f"Web Interactor Tool Started successfully with the goal: {goal}"
        # return {"action":"done"}

