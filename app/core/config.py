from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Task Prioritization App"
    API_V1_STR: str = "/api/v1"
    
    # Database settings
    DATABASE_URL: str
    
    # OpenAI settings
    OPENAI_API_KEY: str
    
    # Cache settings
    CACHE_EXPIRE_TIME: int = 1800  # 30 minutter i sekunder
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings() 