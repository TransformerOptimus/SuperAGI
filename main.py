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
from datetime import timedelta, datetime
from superagi.agent.workflow_seed import IterationWorkflowSeed, AgentWorkflowSeed
from superagi.config.config import get_config
from superagi.controllers.agent import router as agent_router
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
from superagi.controllers.knowledges import router as knowledges_router
from superagi.controllers.knowledge_configs import router as knowledge_configs_router
from superagi.controllers.vector_dbs import router as vector_dbs_router
from superagi.controllers.vector_db_indices import router as vector_db_indices_router
from superagi.controllers.marketplace_stats import router as marketplace_stats_router
from superagi.controllers.api_key import router as api_key_router
from superagi.controllers.api.agent import router as api_agent_router
from superagi.controllers.webhook import router as web_hook_router
from superagi.helper.tool_helper import register_toolkits, register_marketplace_toolkits
from superagi.lib.logger import logger
from superagi.llms.google_palm import GooglePalm
from superagi.llms.openai import OpenAi
from superagi.models.agent_template import AgentTemplate
from superagi.models.organisation import Organisation
from superagi.models.types.login_request import LoginRequest
from superagi.models.types.validate_llm_api_key_request import ValidateAPIKeyRequest
from superagi.models.user import User
from superagi.models.workflows.agent_workflow import AgentWorkflow
from superagi.models.workflows.iteration_workflow import IterationWorkflow
from superagi.models.workflows.iteration_workflow_step import IterationWorkflowStep
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
app.include_router(knowledges_router, prefix="/knowledges")
app.include_router(knowledge_configs_router, prefix="/knowledge_configs")
app.include_router(vector_dbs_router, prefix="/vector_dbs")
app.include_router(vector_db_indices_router, prefix="/vector_db_indices")
app.include_router(marketplace_stats_router, prefix="/marketplace")
app.include_router(api_key_router, prefix="/api-keys")
app.include_router(api_agent_router,prefix="/v1/agent")
app.include_router(web_hook_router,prefix="/webhook")

# in production you can use Settings management
# from pydantic to get secret key from .env
class Settings(BaseModel):
    # jwt_secret = get_config("JWT_SECRET_KEY")
    authjwt_secret_key: str = superagi.config.config.get_config("JWT_SECRET_KEY")


def create_access_token(email, Authorize: AuthJWT = Depends()):
    expiry_time_hours = superagi.config.config.get_config("JWT_EXPIRY")
    if type(expiry_time_hours) == str:
        expiry_time_hours = int(expiry_time_hours)
    if expiry_time_hours is None:
        expiry_time_hours = 200
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


def replace_old_iteration_workflows(session):
    templates = session.query(AgentTemplate).all()
    for template in templates:
        iter_workflow = IterationWorkflow.find_by_id(session, template.agent_workflow_id)
        if not iter_workflow:
            continue
        if iter_workflow.name == "Fixed Task Queue":
            agent_workflow = AgentWorkflow.find_by_name(session, "Fixed Task Workflow")
            template.agent_workflow_id = agent_workflow.id
            session.commit()

        if iter_workflow.name == "Maintain Task Queue":
            agent_workflow = AgentWorkflow.find_by_name(session, "Dynamic Task Workflow")
            template.agent_workflow_id = agent_workflow.id
            session.commit()

        if iter_workflow.name == "Don't Maintain Task Queue" or iter_workflow.name == "Goal Based Agent":
            agent_workflow = AgentWorkflow.find_by_name(session, "Goal Based Workflow")
            template.agent_workflow_id = agent_workflow.id
            session.commit()

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

    def register_toolkit_for_all_organisation():
        organizations = session.query(Organisation).all()
        for organization in organizations:
            register_toolkits(session, organization)
        logger.info("Successfully registered local toolkits for all Organisations!")

    def register_toolkit_for_master_organisation():
        marketplace_organisation_id = superagi.config.config.get_config("MARKETPLACE_ORGANISATION_ID")
        marketplace_organisation = session.query(Organisation).filter(
            Organisation.id == marketplace_organisation_id).first()
        if marketplace_organisation is not None:
            register_marketplace_toolkits(session, marketplace_organisation)

    IterationWorkflowSeed.build_single_step_agent(session)
    IterationWorkflowSeed.build_task_based_agents(session)
    IterationWorkflowSeed.build_action_based_agents(session)
    IterationWorkflowSeed.build_initialize_task_workflow(session)

    AgentWorkflowSeed.build_goal_based_agent(session)
    AgentWorkflowSeed.build_task_based_agent(session)
    AgentWorkflowSeed.build_fixed_task_based_agent(session)
    AgentWorkflowSeed.build_sales_workflow(session)
    AgentWorkflowSeed.build_recruitment_workflow(session)
    AgentWorkflowSeed.build_coding_workflow(session)

    # NOTE: remove old workflows. Need to remove this changes later
    workflows = ["Sales Engagement Workflow", "Recruitment Workflow", "SuperCoder", "Goal Based Workflow",
     "Dynamic Task Workflow", "Fixed Task Workflow"]
    workflows = session.query(AgentWorkflow).filter(AgentWorkflow.name.not_in(workflows))
    for workflow in workflows:
        session.delete(workflow)

    # AgentWorkflowSeed.doc_search_and_code(session)
    # AgentWorkflowSeed.build_research_email_workflow(session)
    replace_old_iteration_workflows(session)

    if env != "PROD":
        register_toolkit_for_all_organisation()
    else:
        register_toolkit_for_master_organisation()
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


@app.post("/validate-llm-api-key")
async def validate_llm_api_key(request: ValidateAPIKeyRequest, Authorize: AuthJWT = Depends()):
    """API to validate LLM API Key"""
    source = request.model_source
    api_key = request.model_api_key
    valid_api_key = False
    if source == "OpenAi":
        valid_api_key = OpenAi(api_key=api_key).verify_access_key()
    elif source == "Google Palm":
        valid_api_key = GooglePalm(api_key=api_key).verify_access_key()
    if valid_api_key:
        return {"message": "Valid API Key", "status": "success"}
    else:
        return {"message": "Invalid API Key", "status": "failed"}


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

@app.get('/get/github_client_id')
def github_client_id():
    """Get GitHub Client ID"""

    git_hub_client_id = superagi.config.config.get_config("GITHUB_CLIENT_ID")
    if git_hub_client_id:
        git_hub_client_id = git_hub_client_id.strip()
    return {"github_client_id": git_hub_client_id}

# # __________________TO RUN____________________________
# # uvicorn main:app --host 0.0.0.0 --port 8001 --reload

