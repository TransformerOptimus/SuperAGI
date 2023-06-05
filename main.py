from fastapi import FastAPI, HTTPException, Depends, Request,status,Query
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi.responses import RedirectResponse
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
from superagi.models.project import Project
from superagi.models.user import User
from superagi.models.organisation import Organisation
from fastapi_sqlalchemy import DBSessionMiddleware, db
from superagi.models.base_model import DBBaseModel
from superagi.models.types.login_request import LoginRequest
from superagi.controllers.user import router as user_router
from superagi.controllers.organisation import router as organisation_router
from superagi.controllers.project import router as project_router
from superagi.controllers.budget import router as budget_router
from superagi.controllers.agent import router as agent_router
from superagi.controllers.agent_config import router as agent_config_router
from superagi.controllers.agent_execution import router as agent_execution_router
from superagi.controllers.agent_execution_feed import router as agent_execution_feed_router
from superagi.controllers.resources import router as resources_router
from superagi.controllers.tool import router as tool_router
from fastapi.middleware.cors import CORSMiddleware
from superagi.models.tool import Tool
from sqlalchemy import create_engine
from superagi.config.config import get_config
from sqlalchemy.orm import sessionmaker, query
from superagi.tools.base_tool import BaseTool
import os
import inspect
import requests



app = FastAPI()

database_url = get_config('POSTGRES_URL')
db_username = get_config('DB_USERNAME')
db_password = get_config('DB_PASSWORD')
db_name = get_config('DB_NAME')

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
    "http://localhost:3001",
    "http://localhost:3000",
    # Add more origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
app.include_router(resources_router, prefix="/resources")

# in production you can use Settings management
# from pydantic to get secret key from .env
class Settings(BaseModel):
    authjwt_secret_key: str = "secret"
    # authjwt_secret_key: str = get_config("JWT_SECRET_KEY")

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


Session = sessionmaker(bind=engine)
session = Session()
organisation = session.query(Organisation).filter_by(id=1).first()

if not organisation or organisation is None:
    organisation = Organisation(id=1, name='Default Organization',
                                        description='This is the default organization')
    session.add(organisation)
    session.commit()

project_name = "Default Project"
project = session.query(Project).filter_by(name="Default Project", organisation_id=organisation.id).first()
# project = Project.query.filter_by(name=project, organisation_id=org.id).first()
if project is None:
    project = Project(name=project_name, description=project_name, organisation_id=organisation.id)
    session.add(project)
    session.commit()


def add_or_update_tool(db: Session, tool_name: str, folder_name: str, class_name: str, file_name: str):
    # Check if a record with the given tool name already exists
    tool = db.query(Tool).filter_by(name=tool_name).first()

    if tool:
        # Update the attributes of the existing tool record
        tool.folder_name = folder_name
        tool.class_name = class_name
        tool.file_name = file_name
    else:
        # Create a new tool record
        tool = Tool(name=tool_name, folder_name=folder_name, class_name=class_name, file_name=file_name)
        db.add(tool)

    db.commit()
    return tool


def get_classes_in_file(file_path):
    classes = []

    # Load the module from the file
    module = load_module_from_file(file_path)

    # Iterate over all members of the module
    for name, member in inspect.getmembers(module):
        # Check if the member is a class and extends BaseTool
        if inspect.isclass(member) and issubclass(member, BaseTool) and member != BaseTool:
            class_dict = {}
            class_dict['class_name'] = member.__name__

            class_obj = getattr(module, member.__name__)
            try:
                obj = class_obj()
                class_dict['class_attribute'] = obj.name
            except:
                class_dict['class_attribute'] = None

            classes.append(class_dict)
    return classes


def load_module_from_file(file_path):
    import importlib.util

    spec = importlib.util.spec_from_file_location("module_name", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


# Function to process the files and extract class information
def process_files(folder_path):
    existing_tools = session.query(Tool).all()
    existing_tools = [Tool(id=None, name=tool.name, folder_name=tool.folder_name, class_name=tool.class_name) for tool
                      in existing_tools]

    new_tools = []
    # Iterate over all subfolders
    for folder_name in os.listdir(folder_path):
        folder_dir = os.path.join(folder_path, folder_name)

        if os.path.isdir(folder_dir):
            # Iterate over all files in the subfolder
            for file_name in os.listdir(folder_dir):
                file_path = os.path.join(folder_dir, file_name)
                if file_name.endswith(".py") and not file_name.startswith("__init__"):
                    # Get clasess
                    classes = get_classes_in_file(file_path=file_path)
                    # filtered_classes = [clazz for clazz in classes if
                    #                     clazz["class_name"].endswith("Tool") and clazz["class_name"] != "BaseTool"]
                    for clazz in classes:
                        new_tool = Tool(class_name=clazz["class_name"], folder_name=folder_name, file_name=file_name,
                                        name=clazz["class_attribute"])
                        new_tools.append(new_tool)

    for tool in new_tools:
        add_or_update_tool(session, tool_name=tool.name, file_name=tool.file_name, folder_name=tool.folder_name,
                           class_name=tool.class_name)


# Specify the folder path
folder_path = "superagi/tools"

# Process the files and store class information
process_files(folder_path)
session.close()


# Specify the folder path
folder_path = "superagi/tools"

# Process the files and store class information
process_files(folder_path)
session.close()

@app.post('/login')
def login(request: LoginRequest, Authorize: AuthJWT = Depends()):
    email_to_find = request.email
    user:User = db.session.query(User).filter(User.email == email_to_find).first()

    if user ==None or request.email != user.email or request.password != user.password:
        raise HTTPException(status_code=401,detail="Bad username or password")

    # subject identifier for who this token is for example id or username from database
    access_token = Authorize.create_access_token(subject=user.email)
    return {"access_token": access_token}


# def get_jwt_from_payload(user_email: str,Authorize: AuthJWT = Depends()):
#     access_token = Authorize.create_access_token(subject=user_email)
#     return access_token

@app.get('/github-login')
def github_login():
    github_client_id = ""
    return RedirectResponse(f'https://github.com/login/oauth/authorize?scope=user:email&client_id={github_client_id}')

@app.get('/github-auth')
def github_auth_handler(code: str = Query(...),Authorize: AuthJWT = Depends()):
    github_token_url = 'https://github.com/login/oauth/access_token'
    github_client_id = ""
    github_client_secret = ""
    frontend_url = "http://localhost:3000"
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
            db_user: User = db.session.query(User).filter(User.email == user_data["email"]).first()
            if db_user is None:
                user = User(name=user_data["name"], email=user_data["email"])
                db.session.add(user)
                db.session.commit()
            if user_data["email"] is not None:
                jwt_token = Authorize.create_access_token(user_data["email"])
            else:
                jwt_token = Authorize.create_access_token(user_data["login"])
            redirect_url_success = f"{frontend_url}?access_token={jwt_token}"
            # redirect_url_success = "https://superagi.com/"
            return RedirectResponse(url=redirect_url_success)
        else:
            redirect_url_failure = "https://superagi.com/"
            return RedirectResponse(url=redirect_url_failure)
    else:
        redirect_url_failure = "https://superagi.com/"
        return RedirectResponse(url=redirect_url_failure)


@app.get('/user')
def user(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    return {"user": current_user}


@app.get("/validate-access-token")
async def root(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        return {
            "message": "token is valid"
        }
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")









# #Unprotected route
# @app.get("/hello/{name}")
# async def say_hello(name: str,):
#     return {"message": f"Hello {name}"}


# # __________________TO RUN____________________________
# # uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# # from superagi.task_queue.celery_app import test_fucntion
