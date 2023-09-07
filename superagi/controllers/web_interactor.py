import json
from pathlib import Path

import requests
from fastapi import APIRouter, Request
from fastapi_sqlalchemy import db

from superagi.agent.common_types import WebActionExecutorResponse
from superagi.jobs.agent_executor import AgentExecutor
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_execution_config import AgentExecutionConfiguration
from superagi.models.workflows.agent_workflow_step import AgentWorkflowStep
from superagi.models.workflows.agent_workflow_step_tool import AgentWorkflowStepTool

router = APIRouter()

import execjs
# Define the JavaScript code as a string

js_file_path = './dom_extractor.js'
# Read the JavaScript code from the file
f = open(js_file_path, "r")
js_code = f.read()
# print(f.read())
# with open(js_file_path, 'r') as js_file:
#     js_code = js_file.read()
#     js_file.close()
# Create an ExecJS context



# Call the JavaScript function and get the result

# Print the result
# print("Result from JavaScript:", result)
@router.get('/execution')
def get_web_pending_execution():
    """Get Web Pending Executions"""
    pending_execution = db.session.query(AgentExecution).filter(AgentExecution.status == "FRONTEND_WAIT") \
        .order_by(AgentExecution.created_at.desc()).first()
    if pending_execution is None:
        return {"agent_execution_id": None}
    return {"agent_execution_id": pending_execution.id}


@router.post('/get_next_action')
async def web_interactor_next_action(request: Request):
    context = execjs.compile(js_code)
    # agent_execution_id = action_obj.agent_execution_id
    # dom_content = action_obj.dom_content
    # last_action_status = action_obj.last_action_status
    body = await request.json()
    # # iterate over the body to get the form data
    print("bodyyyyyyyy",body)
    # items = body.getlist(' name')

    agent_execution_id = body["agent_execution_id"]
    last_action_status = body["last_action_status"]
    last_action = body["last_action"]
    page_url = body["page_url"]
    execution = AgentExecution().get_agent_execution_from_id(db.session, agent_execution_id)

    curr_agent_step_id = execution.current_agent_step_id
    print(curr_agent_step_id, "curr_agent_step_id")

    db_agent_workflow_step = db.session.query(AgentWorkflowStep).filter(
        AgentWorkflowStep.id == curr_agent_step_id).first()
    # print(db_agent_workflow_step, "db_agent_workflow_step")

    action_ref_id = db_agent_workflow_step.action_reference_id
    print(action_ref_id, "action_ref_id")

    db_agent_workflow_step_tool = db.session.query(AgentWorkflowStepTool).filter(
        AgentWorkflowStepTool.id == action_ref_id).first()
    # print(db_agent_workflow_step_tool, "db_agent_workflow_step_tool")

    goal = db_agent_workflow_step_tool.input_instruction
    url = "http://web_interactor:7000/transformed_html"
    request_body = {
        "dom_content": body["dom_content"],
        "goal": goal
    }
    response = requests.post( url, json=request_body)
    print("asdkjasdhfkjsdfhsgdfjhgsjdf",response.json())
    response = response.json()
    transformed_html = response["transformed_dom"]
    dom_content = ""
    if len(transformed_html) != 0:
        dom_content = transformed_html
    if execution is None or execution.status == "COMPLETED":
        return {"status": "COMPLETED"}
    AgentExecutionConfiguration().add_or_update_agent_execution_config(db.session, execution,
                                                                       {"dom_content": dom_content,
                                                                        "last_action": last_action,
                                                                        "page_url": page_url,
                                                                        "last_action_status": last_action_status})
    if execution.status == "COMPLETED":
        return {"status": "COMPLETED"}
    execution.status = "RUNNING"
    db.session.commit()
    response = AgentExecutor().execute_next_step(agent_execution_id)
    print("RESPONSE HERE", response)
    if "Tool WebInteractor returned:" in str(response):
        response = response.result.split("Tool WebInteractor returned:")[1]
        response = response.strip()
        response = json.loads(response)
        response["status"] = "COMPLETED"
        print("CHECEK HERE TOO", response)
        action_reference_element = 0
        if "action_reference_element" in response and response["action_reference_element"] is not None:
            action_reference_element = response["action_reference_element"]
        action_reference_param = ""
        if "action_reference_param" in response and response["action_reference_param"] is not None:
            action_reference_param =response["action_reference_param"]
        response1 = WebActionExecutorResponse(action=response["action"], status=response["status"], action_reference_element= action_reference_element, action_reference_param= action_reference_param, thoughts=response["thoughts"])
        print("YOO",response1)
        execution = AgentExecution().get_agent_execution_from_id(db.session, agent_execution_id)
        if(execution.status=="COMPLETED"):
            response1.status="AGENT_COMPLETED"
        # if response["action_reference_element"] is None:
        #     response1.action_reference_element = 0
        return response1
    else:
        print("*****else response",response)
        response = json.loads(response)
        response = WebActionExecutorResponse(action=response["action"], status=response["status"],
                                             action_reference_element=response["action_reference_element"],
                                             action_reference_param=response["action_reference_param"],
                                             thoughts=response["thoughts"])
        print("THIS IS THE ENDPOINT RESPONSE", response, type(response))
        if response.status == "COMPLETED":
            execution.status = "COMPLETED"
        else:
            execution = AgentExecution().get_agent_execution_from_id(db.session, agent_execution_id)
            execution.status = "FRONTEND_WAIT"
        print(execution.status)
        db.session.commit()
        db.session.flush()
        return response
