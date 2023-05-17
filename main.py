from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
from superagi.models.user import User
from pydantic_sqlalchemy import sqlalchemy_to_pydantic



app = FastAPI()


from superagi.models.db import engine,connectDB
# from base_model import BaseModel
from sqlalchemy.orm import sessionmaker


engine = connectDB()
Session = sessionmaker(bind=engine)
session = Session()


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

# provide a method to create access tokens. The create_access_token()
# function is used to actually generate the token to use authorization
# later in endpoint protected
class LoginRequest(BaseModel):
    email:str
    password:str

@app.post('/login')
def login(request:LoginRequest, Authorize: AuthJWT = Depends()):
    email_to_find = request.email
    user:User = session.query(User).filter(User.email == email_to_find).first()

    if user ==None or request.email != user.email or request.password != user.password:
        raise HTTPException(status_code=401,detail="Bad username or password")

    # subject identifier for who this token is for example id or username from database
    access_token = Authorize.create_access_token(subject=user.email)
    return {"access_token": access_token}


# protect endpoint with function jwt_required(), which requires
# a valid access token in the request headers to access.
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



session.commit()
session.close()

# __________________TO RUN____________________________
# uvicorn main:app --host 0.0.0.0 --port 8001 --reload