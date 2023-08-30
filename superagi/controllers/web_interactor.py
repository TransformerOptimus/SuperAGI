import json

from fastapi import APIRouter, Request
from fastapi_sqlalchemy import db

from superagi.agent.common_types import WebActionExecutorResponse
from superagi.jobs.agent_executor import AgentExecutor
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_execution_config import AgentExecutionConfiguration

router = APIRouter()


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
    # agent_execution_id = action_obj.agent_execution_id
    # dom_content = action_obj.dom_content
    # last_action_status = action_obj.last_action_status
    body = await request.form()
    # iterate over the body to get the form data
    items = body.getlist(' name')
    dom_content = ""
    agent_execution_id = ""
    last_action_status = ""
    last_action = ""
    page_url = ""
    print("ITEMSSSSS", items)
    for item in items:
        if item[1:12] == "dom_content":
            dom_content = item[17:]
        elif item[1:19] == "agent_execution_id":
            agent_execution_id = item[24:]
        elif item[1:19] == "last_action_status":
            last_action_status = item[24:]
        elif item[1:12] == "last_action":
            last_action = item[17:]
        elif item[1:9] == "page_url":
            page_url = item[14:]
        elif item[1:19] == "last_action_status":
            last_action_status = item[24:]
    dom_content = dom_content.split("------WebKitFormBoundary")[0]
    last_action = last_action.split("------WebKitFormBoundary")[0]
    page_url = page_url.split("------WebKitFormBoundary")[0]
    agent_execution_id = agent_execution_id.split('\n')[0]
    last_action_status = last_action_status.split('\n')[0]
    print("dom content", dom_content)

    execution = AgentExecution().get_agent_execution_from_id(db.session, agent_execution_id)

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
        if action_reference_element is not None:
            action_reference_element = int(action_reference_element)
        response1 = WebActionExecutorResponse(action=response["action"], status=response["status"], action_reference_element= action_reference_element, action_reference_param= response["action_reference_param"], thoughts=response["thoughts"])
        execution = AgentExecution().get_agent_execution_from_id(db.session, agent_execution_id)
        if(execution.status=="COMPLETED"):
            response1.status="AGENT_COMPLETED"
        if response["action_reference_element"] is None:
            response1.action_reference_element = 0
        return response1
    else:
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
