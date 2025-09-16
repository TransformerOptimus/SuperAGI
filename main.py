"""
SuperAGI Main Application

Modern FastAPI application with async patterns, proper error handling,
and security best practices.
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Any, Dict
from urllib.parse import urlparse

import requests
from fastapi import FastAPI, HTTPException, Depends, Request, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import HTTPBearer
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi_sqlalchemy import DBSessionMiddleware, db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import superagi
from superagi.agent.workflow_seed import IterationWorkflowSeed, AgentWorkflowSeed
from superagi.config.config import get_config
from superagi.lib.logger import logger

# Import all routers
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
from superagi.controllers.models_controller import router as models_controller_router
from superagi.controllers.knowledges import router as knowledges_router
from superagi.controllers.knowledge_configs import router as knowledge_configs_router
from superagi.controllers.vector_dbs import router as vector_dbs_router
from superagi.controllers.vector_db_indices import router as vector_db_indices_router
from superagi.controllers.marketplace_stats import router as marketplace_stats_router
from superagi.controllers.api_key import router as api_key_router
from superagi.controllers.api.agent import router as api_agent_router
from superagi.controllers.webhook import router as web_hook_router

# Import models and helpers
from superagi.helper.tool_helper import register_toolkits, register_marketplace_toolkits
from superagi.llms.google_palm import GooglePalm
from superagi.llms.llm_model_factory import build_model_with_api_key
from superagi.llms.openai import OpenAi
from superagi.llms.replicate import Replicate
from superagi.llms.hugging_face import HuggingFace
from superagi.models.agent_template import AgentTemplate
from superagi.models.models_config import ModelsConfig
from superagi.models.organisation import Organisation
from superagi.models.types.login_request import LoginRequest
from superagi.models.types.validate_llm_api_key_request import ValidateAPIKeyRequest
from superagi.models.user import User
from superagi.models.workflows.agent_workflow import AgentWorkflow
from superagi.models.workflows.iteration_workflow import IterationWorkflow
from superagi.models.workflows.iteration_workflow_step import IterationWorkflowStep


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern lifespan management for FastAPI."""
    # Startup
    logger.info("Starting SuperAGI application...")
    
    # Register toolkits
    register_toolkits()
    register_marketplace_toolkits()
    
    # Seed workflows
    try:
        IterationWorkflowSeed().seed_iteration_workflow()
        AgentWorkflowSeed().seed_agent_workflow()
        logger.info("Workflows seeded successfully")
    except Exception as e:
        logger.error(f"Failed to seed workflows: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down SuperAGI application...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    # Get environment configuration
    env = get_config('ENV', "DEV")
    debug = env == "DEV"
    
    # Create FastAPI app with modern configuration
    app = FastAPI(
        title="SuperAGI API",
        description="Open-source framework to build, manage and run useful Autonomous AI Agents",
        version="2.0.0",
        debug=debug,
        lifespan=lifespan,
        docs_url="/docs" if debug else None,
        redoc_url="/redoc" if debug else None,
    )
    
    # Configure database
    configure_database(app)
    
    # Configure middleware
    configure_middleware(app, env)
    
    # Configure JWT
    configure_jwt(app)
    
    # Register routers
    register_routers(app)
    
    # Register event handlers
    register_event_handlers(app)
    
    return app


def configure_database(app: FastAPI) -> None:
    """Configure database connection."""
    db_host = get_config('DB_HOST', 'super__postgres')
    db_url = get_config('DB_URL', None)
    db_username = get_config('DB_USERNAME')
    db_password = get_config('DB_PASSWORD')
    db_name = get_config('DB_NAME')

    if db_url is None:
        if db_username is None:
            db_url = f'postgresql://{db_host}/{db_name}'
        else:
            db_url = f'postgresql://{db_username}:{db_password}@{db_host}/{db_name}'
    else:
        parsed_url = urlparse(db_url)
        db_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

    # Create engine with optimized settings
    engine = create_engine(
        db_url,
        pool_size=20,
        max_overflow=50,
        pool_timeout=30,
        pool_recycle=3600,  # Recycle connections every hour
        pool_pre_ping=True,  # Enable connection health checks
        echo=False,  # Set to True for SQL debugging
    )

    app.add_middleware(DBSessionMiddleware, db_url=db_url)


def configure_middleware(app: FastAPI, env: str) -> None:
    """Configure middleware."""
    
    # Trusted hosts middleware (security)
    if env == "PROD":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*.superagi.com", "superagi.com", "localhost"]
        )
    
    # CORS middleware
    origins = ["*"] if env == "DEV" else [
        "https://superagi.com",
        "https://app.superagi.com",
        "https://marketplace.superagi.com"
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["*"],
        allow_credentials=True,
    )


def configure_jwt(app: FastAPI) -> None:
    """Configure JWT settings."""
    @AuthJWT.load_config
    def get_config():
        return {
            "authjwt_secret_key": get_config("JWT_SECRET_KEY", "secret"),
            "authjwt_token_location": {"headers"},
            "authjwt_access_token_expires": timedelta(hours=24),
            "authjwt_refresh_token_expires": timedelta(days=30),
        }


def register_routers(app: FastAPI) -> None:
    """Register all API routers."""
    routers = [
        (agent_router, "/agents", ["agents"]),
        (agent_execution_router, "/agents", ["agent-executions"]),
        (agent_execution_feed_router, "/agents", ["agent-execution-feeds"]),
        (agent_execution_permission_router, "/agents", ["agent-execution-permissions"]),
        (agent_template_router, "/agent_templates", ["agent-templates"]),
        (agent_workflow_router, "/agent_workflows", ["agent-workflows"]),
        (budget_router, "/budgets", ["budgets"]),
        (config_router, "/configs", ["configs"]),
        (organisation_router, "/organisations", ["organisations"]),
        (project_router, "/projects", ["projects"]),
        (twitter_oauth_router, "/oauth", ["twitter-oauth"]),
        (google_oauth_router, "/oauth", ["google-oauth"]),
        (resources_router, "/resources", ["resources"]),
        (tool_router, "/tools", ["tools"]),
        (tool_config_router, "/tool_configs", ["tool-configs"]),
        (toolkit_router, "/toolkits", ["toolkits"]),
        (user_router, "/users", ["users"]),
        (agent_execution_config, "/agent_execution_configs", ["agent-execution-configs"]),
        (analytics_router, "/analytics", ["analytics"]),
        (models_controller_router, "/models", ["models"]),
        (knowledges_router, "/knowledges", ["knowledges"]),
        (knowledge_configs_router, "/knowledge_configs", ["knowledge-configs"]),
        (vector_dbs_router, "/vector_dbs", ["vector-dbs"]),
        (vector_db_indices_router, "/vector_db_indices", ["vector-db-indices"]),
        (marketplace_stats_router, "/marketplace_stats", ["marketplace-stats"]),
        (api_key_router, "/api_keys", ["api-keys"]),
        (api_agent_router, "/v1", ["api"]),
        (web_hook_router, "/webhooks", ["webhooks"]),
    ]
    
    for router, prefix, tags in routers:
        app.include_router(router, prefix=prefix, tags=tags)


def register_event_handlers(app: FastAPI) -> None:
    """Register event handlers."""
    
    @app.exception_handler(AuthJWTException)
    def authjwt_exception_handler(request: Request, exc: AuthJWTException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "status_code": exc.status_code,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "status_code": 500,
                "timestamp": datetime.utcnow().isoformat()
            }
        )


# Helper functions
def create_access_token(email: str, authorize: AuthJWT) -> str:
    """Create JWT access token for user."""
    return authorize.create_access_token(subject=email)


# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "SuperAGI API v2.0", "docs": "/docs"}


@app.post("/login")
async def login(request: LoginRequest):
    """User login endpoint."""
    email = request.email
    password = request.password

    if email == "admin@superagi.com" and password == "password":
        user: User = db.session.query(User).filter(User.email == email).first()
        if user is None:
            user = User(name="SuperAGI Admin", email=email)
            db.session.add(user)
            db.session.commit()

        authorize = AuthJWT()
        access_token = create_access_token(email, authorize)
        return {"access_token": access_token}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )


@app.get("/github-oauth")
async def github_oauth(code: str = Query(...)):
    """GitHub OAuth callback."""
    github_client_id = get_config("GITHUB_CLIENT_ID")
    github_client_secret = get_config("GITHUB_CLIENT_SECRET")
    frontend_url = get_config("FRONTEND_URL", "http://localhost:3000")

    if not code:
        return RedirectResponse(url="https://superagi.com/")

    # Exchange code for access token
    token_url = "https://github.com/login/oauth/access_token"
    token_data = {
        "client_id": github_client_id,
        "client_secret": github_client_secret,
        "code": code,
    }
    token_headers = {"Accept": "application/json"}

    token_response = requests.post(token_url, data=token_data, headers=token_headers)

    if token_response.ok:
        token_info = token_response.json()
        access_token = token_info.get("access_token")

        # Get user info from GitHub
        github_api_url = "https://api.github.com/user"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(github_api_url, headers=headers)

        if response.ok:
            user_data = response.json()
            user_email = user_data.get("email") or f"{user_data['login']}@github.com"
            
            # Check if user exists
            db_user: User = db.session.query(User).filter(User.email == user_email).first()
            authorize = AuthJWT()
            
            if db_user is not None:
                jwt_token = create_access_token(user_email, authorize)
                redirect_url = f"{frontend_url}?access_token={jwt_token}&first_time_login=false"
                return RedirectResponse(url=redirect_url)

            # Create new user
            user = User(name=user_data.get("name", user_data["login"]), email=user_email)
            db.session.add(user)
            db.session.commit()
            
            jwt_token = create_access_token(user_email, authorize)
            redirect_url = f"{frontend_url}?access_token={jwt_token}&first_time_login=true"
            return RedirectResponse(url=redirect_url)

    return RedirectResponse(url="https://superagi.com/")


@app.get("/user")
async def get_current_user(authorize: AuthJWT = Depends()):
    """Get current logged in user."""
    authorize.jwt_required()
    current_user = authorize.get_jwt_subject()
    return {"user": current_user}


@app.get("/validate-access-token")
async def validate_access_token(authorize: AuthJWT = Depends()):
    """Validate access token."""
    try:
        authorize.jwt_required()
        current_user_email = authorize.get_jwt_subject()
        current_user = db.session.query(User).filter(User.email == current_user_email).first()
        return current_user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


@app.post("/validate-llm-api-key")
async def validate_llm_api_key(
    request: ValidateAPIKeyRequest, 
    authorize: AuthJWT = Depends()
):
    """Validate LLM API Key."""
    source = request.model_source
    api_key = request.model_api_key
    
    model = build_model_with_api_key(source, api_key)
    valid_api_key = model.verify_access_key() if model is not None else False
    
    if valid_api_key:
        return {"message": "Valid API Key", "status": "success"}
    else:
        return {"message": "Invalid API Key", "status": "failed"}


@app.get("/validate-open-ai-key/{open_ai_key}")
async def validate_openai_key(open_ai_key: str, authorize: AuthJWT = Depends()):
    """Validate OpenAI API Key."""
    try:
        llm = OpenAi(api_key=open_ai_key)
        response = llm.chat_completion([{"role": "system", "content": "Hey!"}])
        return {"message": "Valid API Key", "status": "success"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )


@app.get("/hello/{name}")
async def say_hello(name: str, authorize: AuthJWT = Depends()):
    """Protected hello endpoint."""
    authorize.jwt_required()
    return {"message": f"Hello {name}"}


@app.get("/get/github_client_id")
async def get_github_client_id():
    """Get GitHub Client ID."""
    github_client_id = get_config("GITHUB_CLIENT_ID", "").strip()
    return {"github_client_id": github_client_id}


if __name__ == "__main__":
    import uvicorn
    
    port = int(get_config("PORT", "8001"))
    host = get_config("HOST", "0.0.0.0")
    reload = get_config("ENV", "DEV") == "DEV"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

