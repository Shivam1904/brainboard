import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # FastAPI
    app_name: str = "Brainboard API"
    debug: bool = True
    
    # AWS
    aws_region: str = "us-east-1"
    dynamodb_table_reminders: str = "brainboard-reminders"
    dynamodb_table_summaries: str = "brainboard-summaries"
    dynamodb_table_users: str = "brainboard-users"
    
    # Authentication
    cognito_user_pool_id: Optional[str] = None
    cognito_client_id: Optional[str] = None
    jwt_secret_key: str = "your-secret-key-here"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    
    # External APIs
    openai_api_key: Optional[str] = None
    serper_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()
