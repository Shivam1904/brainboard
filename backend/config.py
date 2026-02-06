import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # App Settings
    APP_TITLE: str = "Brainboard Backend"
    APP_DESCRIPTION: str = "Modular backend for Brainboard application"
    APP_VERSION: str = "1.0.0"
    
    # Server Settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8989"))
    RELOAD: bool = os.getenv("RELOAD", "True").lower() == "true"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./brainboard.db")
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    # API Prefixes
    API_PREFIX: str = "/api/v1"
    
    # Defaults
    DEFAULT_USER_ID: str = "user_001"

settings = Settings()
