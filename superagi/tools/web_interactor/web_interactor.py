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


class WebInteractorSchema(BaseModel):
    # curr_page_url: str = Field(
    #     ...,
    #     description="URL of the page to interact with",
    # )
    goal: str = Field(
        ...,
        description="goal of the current execution"
    )
    # DOM: str = Field(
    #     ...,
    #     description="DOM of the url on which actions have to be performed"
    # )


class WebInteractorTool(BaseTool):
    """
    Web Interactor tool

    Attributes:
        name : The name.
        description : The description.
        args_schema : The args schema.
    """
    llm: Optional[BaseLlm] = None
    name = "WebInteractor"
    agent_execution_id: int = None
    description = (
        "A tool for interacting with web pages and performing actions like button click, typing and web page navigation."
        # "Input should be a search query."
    )
    args_schema: Type[WebInteractorSchema] = WebInteractorSchema

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, goal: str):
        """
        Execute the Web Interactor tool.

        Args:
            goal : Goal of the execution

        Returns:
            JSON object of the form {
              "action": "TYPE",
              "action_reference_element": element_id
              "action_reference_param" : "some text",
              "status":"RUNNING",
              "thoughts":"Why you are taking this action"
            }
        """
        # print("************URL",curr_page_url)
        print(self.agent_execution_id,"**********")
        current_page_url = self.toolkit_config.session.query(AgentExecutionConfiguration).filter(
            AgentExecutionConfiguration.agent_execution_id == self.agent_execution_id,
            AgentExecutionConfiguration.key == 'page_url').first().value

        # print(current_page_url, "*******")
        dom_content = self.toolkit_config.session.query(AgentExecutionConfiguration).filter(
            AgentExecutionConfiguration.agent_execution_id == self.agent_execution_id,
            AgentExecutionConfiguration.key == 'dom_content').first().value

        db_agent_execution = self.toolkit_config.session.query(AgentExecution).filter(
            AgentExecution.id == self.agent_execution_id).first()
        print(db_agent_execution, "db_agent_execution*****")

        curr_agent_step_id = db_agent_execution.current_agent_step_id
        print(curr_agent_step_id, "curr_agent_step_id")

        db_agent_workflow_step = self.toolkit_config.session.query(AgentWorkflowStep).filter(
            AgentWorkflowStep.id == curr_agent_step_id).first()
        print(db_agent_workflow_step, "db_agent_workflow_step")

        action_ref_id = db_agent_workflow_step.action_reference_id
        print(action_ref_id, "action_ref_id")

        db_agent_workflow_step_tool = self.toolkit_config.session.query(AgentWorkflowStepTool).filter(
            AgentWorkflowStepTool.id == action_ref_id).first()
        print(db_agent_workflow_step_tool, "db_agent_workflow_step_tool")

        goal = db_agent_workflow_step_tool.input_instruction
        print(goal, "goal")
        history = AgentExecutionFeed.fetch_agent_execution_feeds(self.toolkit_config.session, self.agent_execution_id)
        history = history.join("/n")
        output_obj = self.get_element_from_llm(current_page_url, goal, dom_content, history)

        # print("************output obj" ,output_obj)
        return output_obj
        # return {"action":"done"}

    def get_element_from_llm(self, curr_page_url: str, goal: str, DOM: str, history: str):
        DOM_element_prompt = """
            History: {history}
            You are a Web Interactor assistant. You have to analyze and understand the given DOM of a web URL. Based on the given goal, you have to give the action to be done. You can perform the following actions: 'click', 'type', 'go to'; so the action must be given according to the available actions and the given DOM.

            goal: `{goal}`
            CLICK: This action is performed when the  given task requires you to click on an element in the DOM
            TYPE: This action is performed when the given task requires you to write text into textboxes, textareas etc.
            GO_TO: This action is performed when the given a task that requires you to go to some other webpage. Basically to change address of current page
            TYPESUBMIT: This action is performed when the given task requires you to write text into textboxes, textareas etc. and then submit the form

            You also need to give the action_reference_element for the action which means you need to provide the integer id which is given in the dom_content.
            Similarly, in case of TYPE AND GO_TO actions, you will have to give the respective action_reference_param which can be used.

            If goal is completed, set status as "COMPLETED" 


            You are currently on `{curr_page_url}`
            This is the given DOM 

            `{DOM}`

            If the above DOM is empty, you should assume that it is a blank web page and hence take actions accordingly

            The next action must very strictly follow the given output JSON format. Please ensure that the output is in this format for best results.
            {
              "action": "TYPE",
              "action_reference_element": element_id
              "action_reference_param" : "some text",
              "thoughts":"Why you are taking this action"
            }"""
        print("************DOM", DOM)
        DOM_element_prompt = DOM_element_prompt.replace("{goal}", str(goal))
        DOM_element_prompt = DOM_element_prompt.replace("{curr_page_url}", curr_page_url)
        DOM_element_prompt = DOM_element_prompt.replace("{DOM}", DOM)
        DOM_element_prompt= DOM_element_prompt.replace("{history}", history)

        messages = [{"role": "system", "content": DOM_element_prompt}]
        result = self.llm.chat_completion(messages, max_tokens=self.max_token_limit)
        return result["content"]