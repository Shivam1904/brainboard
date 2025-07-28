import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # FastAPI
    app_name: str = "Brainboard API"
    debug: bool = True
    
    # Database
    database_url: str = "sqlite:///./brainboard.db"
    
    # API Keys
    openai_api_key: Optional[str] = None
    serper_api_key: Optional[str] = None
    
    # AI Configuration
    default_ai_model: str = "gpt-3.5-turbo"
    max_search_results: int = 5
    max_summary_tokens: int = 400
    
    # Widget Configuration
    default_user_id: str = "default_user"
    widget_max_summaries_history: int = 50
    
    # AWS (for future migration)
    aws_region: str = "us-east-1"
    dynamodb_table_widgets: str = "brainboard-widgets"
    dynamodb_table_summaries: str = "brainboard-summaries"
    
    # Authentication (for future)
    jwt_secret_key: str = "your-secret-key-here"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env file

# Create settings instance
settings = Settings()
