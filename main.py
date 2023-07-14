import os
import pickle
from datetime import datetime, timedelta

import requests
from fastapi import FastAPI, HTTPException, Depends, Request, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi_sqlalchemy import DBSessionMiddleware, db
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import superagi
import urllib.parse
import json
import http.client as http_client
from superagi.helper.twitter_tokens import TwitterTokens
from datetime import datetime, timedelta
from superagi.agent.agent_prompt_builder import AgentPromptBuilder
from superagi.config.config import get_config
from superagi.controllers.agent import router as agent_router
from superagi.controllers.agent_config import router as agent_config_router
from superagi.controllers.agent_execution import router as agent_execution_router
from superagi.controllers.agent_execution_feed import router as agent_execution_feed_router
from superagi.controllers.agent_execution_permission import router as agent_execution_permission_router
from superagi.controllers.agent_template import router as agent_template_router
from superagi.controllers.agent_workflow import router as agent_workflow_router
from superagi.controllers.budget import router as budget_router
from superagi.controllers.config import router as config_router
from superagi.controllers.organisation import router as organisation_router
from superagi.controllers.project import router as project_router
from superagi.controllers.twitter_oauth import router as twitter_oauth_router
from superagi.controllers.google_oauth import router as google_oauth_router
from superagi.controllers.resources import router as resources_router
from superagi.controllers.tool import router as tool_router
from superagi.controllers.tool_config import router as tool_config_router
from superagi.controllers.toolkit import router as toolkit_router
from superagi.controllers.user import router as user_router
from superagi.controllers.agent_execution_config import router as agent_execution_config
from superagi.controllers.analytics import router as analytics_router
from superagi.helper.tool_helper import register_toolkits
from superagi.lib.logger import logger
from superagi.llms.openai import OpenAi
from superagi.helper.auth import get_current_user
from superagi.models.agent_workflow import AgentWorkflow
from superagi.models.agent_workflow_step import AgentWorkflowStep
from superagi.models.organisation import Organisation
from superagi.models.tool_config import ToolConfig
from superagi.models.toolkit import Toolkit
from superagi.models.oauth_tokens import OauthTokens
from superagi.models.types.login_request import LoginRequest
from superagi.models.user import User

app = FastAPI()

database_url = get_config('POSTGRES_URL')
db_username = get_config('DB_USERNAME')
db_password = get_config('DB_PASSWORD')
db_name = get_config('DB_NAME')
env = get_config('ENV', "DEV")

if db_username is None:
    db_url = f'postgresql://{database_url}/{db_name}'
else:
    db_url = f'postgresql://{db_username}:{db_password}@{database_url}/{db_name}'

engine = create_engine(db_url)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# app.add_middleware(DBSessionMiddleware, db_url=f'postgresql://{db_username}:{db_password}@localhost/{db_name}')
app.add_middleware(DBSessionMiddleware, db_url=db_url)

# Configure CORS middleware
origins = [
    # Add more origins if needed
    "*",  # Allow all origins
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Creating requrired tables -- Now handled using migrations
# DBBaseModel.metadata.create_all(bind=engine, checkfirst=True)
# DBBaseModel.metadata.drop_all(bind=engine,checkfirst=True)


app.include_router(user_router, prefix="/users")
app.include_router(tool_router, prefix="/tools")
app.include_router(organisation_router, prefix="/organisations")
app.include_router(project_router, prefix="/projects")
app.include_router(budget_router, prefix="/budgets")
app.include_router(agent_router, prefix="/agents")
app.include_router(agent_config_router, prefix="/agentconfigs")
app.include_router(agent_execution_router, prefix="/agentexecutions")
app.include_router(agent_execution_feed_router, prefix="/agentexecutionfeeds")
app.include_router(agent_execution_permission_router, prefix="/agentexecutionpermissions")
app.include_router(resources_router, prefix="/resources")
app.include_router(config_router, prefix="/configs")
app.include_router(toolkit_router, prefix="/toolkits")
app.include_router(tool_config_router, prefix="/tool_configs")
app.include_router(config_router, prefix="/configs")
app.include_router(agent_template_router, prefix="/agent_templates")
app.include_router(agent_workflow_router, prefix="/agent_workflows")
app.include_router(twitter_oauth_router, prefix="/twitter")
app.include_router(agent_execution_config, prefix="/agent_executions_configs")
app.include_router(analytics_router, prefix="/analytics")

app.include_router(google_oauth_router, prefix="/google")

# in production you can use Settings management
# from pydantic to get secret key from .env
class Settings(BaseModel):
    # jwt_secret = get_config("JWT_SECRET_KEY")
    authjwt_secret_key: str = superagi.config.config.get_config("JWT_SECRET_KEY")


def create_access_token(email, Authorize: AuthJWT = Depends()):
    # expiry_time_hours = get_config("JWT_EXPIRY")
    expiry_time_hours = 1
    expires = timedelta(hours=expiry_time_hours)
    access_token = Authorize.create_access_token(subject=email, expires_time=expires)
    return access_token


# callback to get your configuration
@AuthJWT.load_config
def get_config():
    return Settings()


# exception handler for authjwt
# in production, you can tweak performance using orjson response
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@app.on_event("startup")
async def startup_event():
    # Perform startup tasks here
    logger.info("Running Startup tasks")
    Session = sessionmaker(bind=engine)
    session = Session()
    default_user = session.query(User).filter(User.email == "super6@agi.com").first()
    logger.info(default_user)
    if default_user is not None:
        organisation = session.query(Organisation).filter_by(id=default_user.organisation_id).first()
        logger.info(organisation)
        register_toolkits(session, organisation)

    def build_single_step_agent():
        agent_workflow = session.query(AgentWorkflow).filter(AgentWorkflow.name == "Goal Based Agent").first()

        if agent_workflow is None:
            agent_workflow = AgentWorkflow(name="Goal Based Agent", description="Goal based agent")
            session.add(agent_workflow)
            session.commit()

        # step will have a prompt
        # output of step is either tasks or set commands
        first_step = session.query(AgentWorkflowStep).filter(AgentWorkflowStep.unique_id == "gb1").first()
        output = AgentPromptBuilder.get_super_agi_single_prompt()
        if first_step is None:
            first_step = AgentWorkflowStep(unique_id="gb1",
                                           prompt=output["prompt"], variables=str(output["variables"]),
                                           agent_workflow_id=agent_workflow.id, output_type="tools",
                                           step_type="TRIGGER",
                                           history_enabled=True,
                                           completion_prompt="Determine which next tool to use, and respond using the format specified above:")
            session.add(first_step)
            session.commit()
        else:
            first_step.prompt = output["prompt"]
            first_step.variables = str(output["variables"])
            first_step.output_type = "tools"
            first_step.completion_prompt = "Determine which next tool to use, and respond using the format specified above:"
            session.commit()
        first_step.next_step_id = first_step.id
        session.commit()

    def build_task_based_agents():
        agent_workflow = session.query(AgentWorkflow).filter(AgentWorkflow.name == "Task Queue Agent With Seed").first()
        if agent_workflow is None:
            agent_workflow = AgentWorkflow(name="Task Queue Agent With Seed", description="Task queue based agent")
            session.add(agent_workflow)
            session.commit()

        output = AgentPromptBuilder.start_task_based()

        workflow_step1 = session.query(AgentWorkflowStep).filter(AgentWorkflowStep.unique_id == "tb1").first()
        if workflow_step1 is None:
            workflow_step1 = AgentWorkflowStep(unique_id="tb1",
                                               prompt=output["prompt"], variables=str(output["variables"]),
                                               step_type="TRIGGER",
                                               agent_workflow_id=agent_workflow.id, next_step_id=-1,
                                               output_type="tasks")
            session.add(workflow_step1)
        else:
            workflow_step1.prompt = output["prompt"]
            workflow_step1.variables = str(output["variables"])
            workflow_step1.output_type = "tasks"
            session.commit()

        workflow_step2 = session.query(AgentWorkflowStep).filter(AgentWorkflowStep.unique_id == "tb2").first()
        output = AgentPromptBuilder.create_tasks()
        if workflow_step2 is None:
            workflow_step2 = AgentWorkflowStep(unique_id="tb2",
                                               prompt=output["prompt"], variables=str(output["variables"]),
                                               step_type="NORMAL",
                                               agent_workflow_id=agent_workflow.id, next_step_id=-1,
                                               output_type="tasks")
            session.add(workflow_step2)
        else:
            workflow_step2.prompt = output["prompt"]
            workflow_step2.variables = str(output["variables"])
            workflow_step2.output_type = "tasks"
            session.commit()

        workflow_step3 = session.query(AgentWorkflowStep).filter(AgentWorkflowStep.unique_id == "tb3").first()

        output = AgentPromptBuilder.analyse_task()
        if workflow_step3 is None:
            workflow_step3 = AgentWorkflowStep(unique_id="tb3",
                                               prompt=output["prompt"], variables=str(output["variables"]),
                                               step_type="NORMAL",
                                               agent_workflow_id=agent_workflow.id, next_step_id=-1,
                                               output_type="tools")

            session.add(workflow_step3)
        else:
            workflow_step3.prompt = output["prompt"]
            workflow_step3.variables = str(output["variables"])
            workflow_step3.output_type = "tools"
            session.commit()

        workflow_step4 = session.query(AgentWorkflowStep).filter(AgentWorkflowStep.unique_id == "tb4").first()
        output = AgentPromptBuilder.prioritize_tasks()
        if workflow_step4 is None:
            workflow_step4 = AgentWorkflowStep(unique_id="tb4",
                                               prompt=output["prompt"], variables=str(output["variables"]),
                                               step_type="NORMAL",
                                               agent_workflow_id=agent_workflow.id, next_step_id=-1,
                                               output_type="replace_tasks")

            session.add(workflow_step4)
        else:
            workflow_step4.prompt = output["prompt"]
            workflow_step4.variables = str(output["variables"])
            workflow_step4.output_type = "replace_tasks"
            session.commit()
        session.commit()
        workflow_step1.next_step_id = workflow_step3.id
        workflow_step3.next_step_id = workflow_step2.id
        workflow_step2.next_step_id = workflow_step4.id
        workflow_step4.next_step_id = workflow_step3.id
        session.commit()

    def build_action_based_agents():
        agent_workflow = session.query(AgentWorkflow).filter(AgentWorkflow.name == "Fixed Task Queue").first()
        if agent_workflow is None:
            agent_workflow = AgentWorkflow(name="Fixed Task Queue", description="Fixed Task Queue")
            session.add(agent_workflow)
            session.commit()

        output = AgentPromptBuilder.start_task_based()

        workflow_step1 = session.query(AgentWorkflowStep).filter(AgentWorkflowStep.unique_id == "ab1").first()
        if workflow_step1 is None:
            workflow_step1 = AgentWorkflowStep(unique_id="ab1",
                                               prompt=output["prompt"], variables=str(output["variables"]),
                                               step_type="TRIGGER",
                                               agent_workflow_id=agent_workflow.id, next_step_id=-1,
                                               output_type="tasks")
            session.add(workflow_step1)
        else:
            workflow_step1.prompt = output["prompt"]
            workflow_step1.variables = str(output["variables"])
            workflow_step1.output_type = "tasks"
            workflow_step1.agent_workflow_id = agent_workflow.id
            session.commit()

        workflow_step2 = session.query(AgentWorkflowStep).filter(AgentWorkflowStep.unique_id == "ab2").first()
        output = AgentPromptBuilder.analyse_task()
        if workflow_step2 is None:
            workflow_step2 = AgentWorkflowStep(unique_id="ab2",
                                               prompt=output["prompt"], variables=str(output["variables"]),
                                               step_type="NORMAL",
                                               agent_workflow_id=agent_workflow.id, next_step_id=-1,
                                               output_type="tools")
            session.add(workflow_step2)
        else:
            workflow_step2.prompt = output["prompt"]
            workflow_step2.variables = str(output["variables"])
            workflow_step2.output_type = "tools"
            workflow_step2.agent_workflow_id = agent_workflow.id
            session.commit()

        session.commit()
        workflow_step1.next_step_id = workflow_step2.id
        workflow_step2.next_step_id = workflow_step2.id
        session.commit()

    def check_toolkit_registration():
        organizations = session.query(Organisation).all()
        for organization in organizations:
            register_toolkits(session, organization)
        logger.info("Successfully registered local toolkits for all Organisations!")

    build_single_step_agent()
    build_task_based_agents()
    build_action_based_agents()
    if env != "PROD":
        check_toolkit_registration()
    session.close()


@app.post('/login')
def login(request: LoginRequest, Authorize: AuthJWT = Depends()):
    """Login API for email and password based login"""

    email_to_find = request.email
    user: User = db.session.query(User).filter(User.email == email_to_find).first()

    if user == None or request.email != user.email or request.password != user.password:
        raise HTTPException(status_code=401, detail="Bad username or password")

    # subject identifier for who this token is for example id or username from database
    access_token = create_access_token(user.email, Authorize)
    return {"access_token": access_token}


# def get_jwt_from_payload(user_email: str,Authorize: AuthJWT = Depends()):
#     access_token = Authorize.create_access_token(subject=user_email)
#     return access_token

@app.get('/github-login')
def github_login():
    """GitHub login"""

    github_client_id = ""
    return RedirectResponse(f'https://github.com/login/oauth/authorize?scope=user:email&client_id={github_client_id}')


@app.get('/github-auth')
def github_auth_handler(code: str = Query(...), Authorize: AuthJWT = Depends()):
    """GitHub login callback"""

    github_token_url = 'https://github.com/login/oauth/access_token'
    github_client_id = superagi.config.config.get_config("GITHUB_CLIENT_ID")
    github_client_secret = superagi.config.config.get_config("GITHUB_CLIENT_SECRET")

    frontend_url = superagi.config.config.get_config("FRONTEND_URL", "http://localhost:3000")
    params = {
        'client_id': github_client_id,
        'client_secret': github_client_secret,
        'code': code
    }
    headers = {
        'Accept': 'application/json'
    }
    response = requests.post(github_token_url, params=params, headers=headers)
    if response.ok:
        data = response.json()
        access_token = data.get('access_token')
        github_api_url = 'https://api.github.com/user'
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        response = requests.get(github_api_url, headers=headers)
        if response.ok:
            user_data = response.json()
            user_email = user_data["email"]
            if user_email is None:
                user_email = user_data["login"] + "@github.com"
            db_user: User = db.session.query(User).filter(User.email == user_email).first()
            if db_user is not None:
                jwt_token = create_access_token(user_email, Authorize)
                redirect_url_success = f"{frontend_url}?access_token={jwt_token}"
                return RedirectResponse(url=redirect_url_success)

            user = User(name=user_data["name"], email=user_email)
            db.session.add(user)
            db.session.commit()
            jwt_token = create_access_token(user_email, Authorize)

            redirect_url_success = f"{frontend_url}?access_token={jwt_token}"
            return RedirectResponse(url=redirect_url_success)
        else:
            redirect_url_failure = "https://superagi.com/"
            return RedirectResponse(url=redirect_url_failure)
    else:
        redirect_url_failure = "https://superagi.com/"
        return RedirectResponse(url=redirect_url_failure)


@app.get('/user')
def user(Authorize: AuthJWT = Depends()):
    """API to get current logged in User"""

    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    return {"user": current_user}


@app.get("/validate-access-token")
async def root(Authorize: AuthJWT = Depends()):
    """API to validate access token"""

    try:
        Authorize.jwt_required()
        current_user_email = Authorize.get_jwt_subject()
        current_user = db.session.query(User).filter(User.email == current_user_email).first()
        return current_user
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@app.get("/validate-open-ai-key/{open_ai_key}")
async def root(open_ai_key: str, Authorize: AuthJWT = Depends()):
    """API to validate Open AI Key"""

    try:
        llm = OpenAi(api_key=open_ai_key)
        response = llm.chat_completion([{"role": "system", "content": "Hey!"}])
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")


# #Unprotected route
@app.get("/hello/{name}")
async def say_hello(name: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    return {"message": f"Hello {name}"}

# # __________________TO RUN____________________________
# # uvicorn main:app --host 0.0.0.0 --port 8001 --reload
