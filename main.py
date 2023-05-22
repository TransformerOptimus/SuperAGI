from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
from superagi.models.user import User 
# from superagi.models.user import User 

from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from fastapi_sqlalchemy import DBSessionMiddleware, db
from superagi.models.base_model import DBBaseModel
from superagi.models.types.LoginRequest import LoginRequest
from superagi.controllers.user import router as user_router
from superagi.controllers.organisation import router as organisation_router
from superagi.controllers.project import router as project_router
from superagi.controllers.budget import router as budget_router
from superagi.controllers.agent import router as agent_router
from superagi.controllers.agent_config import router as agent_config_router
from superagi.controllers.agent_execution import router as agent_execution_router
from superagi.controllers.agent_execution_feed import router as agent_execution_feed_router


from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker


app = FastAPI()

db_username = ''
db_password = ''
db_name = ''


db_url = f'postgresql://{db_username}:{db_password}@localhost/{db_name}'
engine = create_engine(db_url)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# app.add_middleware(DBSessionMiddleware, db_url=f'postgresql://{db_username}:{db_password}@localhost/{db_name}')
app.add_middleware(DBSessionMiddleware, db_url=db_url)


DBBaseModel.metadata.create_all(bind=engine,checkfirst=True)
# DBBaseModel.metadata.drop_all(bind=engine,checkfirst=True)


app.include_router(user_router, prefix="/users")
app.include_router(organisation_router, prefix="/organisations")
app.include_router(project_router, prefix="/projects")
app.include_router(budget_router, prefix="/budgets")
app.include_router(agent_router,prefix="/agents")
app.include_router(agent_config_router,prefix="/agentconfigs")
app.include_router(agent_execution_router,prefix="/agentexecutions")
app.include_router(agent_execution_feed_router,prefix="/agentexecutionfeeds")




# in production you can use Settings management
# from pydantic to get secret key from .env
class Settings(BaseModel):
    authjwt_secret_key: str = "secret"

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

@app.post('/login')
def login(request:LoginRequest, Authorize: AuthJWT = Depends()):
    email_to_find = request.email
    user:User = db.session.query(User).filter(User.email == email_to_find).first()

    if user ==None or request.email != user.email or request.password != user.password:
        raise HTTPException(status_code=401,detail="Bad username or password")

    # subject identifier for who this token is for example id or username from database
    access_token = Authorize.create_access_token(subject=user.email)
    return {"access_token": access_token}


@app.get('/user')
def user(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    return {"user": current_user}




@app.get("/")
async def root(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    return {"message": "Hello World"}


#Unprotected route
@app.get("/hello/{name}")
async def say_hello(name: str,):
    return {"message": f"Hello {name}"}



# __________________TO RUN____________________________
# uvicorn main:app --host 0.0.0.0 --port 8001 --reload