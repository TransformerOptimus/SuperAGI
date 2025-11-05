import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/salesagent")

    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Apollo.io
    APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")

    # Email
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    EMAIL_SMTP_HOST = os.getenv("EMAIL_SMTP_HOST", "smtp.gmail.com")
    EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))
    EMAIL_IMAP_SERVER = os.getenv("EMAIL_IMAP_SERVER", "imap.gmail.com")
    EMAIL_SIGNATURE = os.getenv("EMAIL_SIGNATURE", "")

    # Google Search
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

    # Agent
    MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "25"))
    ITERATION_INTERVAL = int(os.getenv("ITERATION_INTERVAL", "300"))
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4")

config = Config()
