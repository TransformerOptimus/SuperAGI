"""
Sales Agent - Main Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import init_db
from api.routes import router

# Create FastAPI app
app = FastAPI(
    title="Sales Agent API",
    description="AI-powered Sales Development Representative (SDR) for B2B outreach and lead generation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["Sales Agent"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("Initializing database...")
    init_db()
    print("Database initialized successfully")


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": "Sales Agent API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
