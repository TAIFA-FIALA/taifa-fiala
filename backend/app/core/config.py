from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:stocksight1484@100.75.201.24:5432/TAIFA_db"
    DATABASE_HOST: str = "100.75.201.24"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "TAIFA_db"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "stocksight1484"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # API Configuration
    SECRET_KEY: str = "ai-africa-funding-development-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8501", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8501"
    ]
    
    # Data Collection Configuration
    RSS_CHECK_INTERVAL_MINUTES: int = 60
    SCRAPING_DELAY_SECONDS: int = 2
    MAX_CONCURRENT_REQUESTS: int = 5
    USER_AGENT: str = "AI-Africa-Funding-Tracker/1.0"
    
    # Email Configuration
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # External APIs
    OPENAI_API_KEY: Optional[str] = None
    GITHUB_TOKEN: Optional[str] = None
    SERPER_DEV_API_KEY: Optional[str] = "33e96f32ac5ee00f408424c4badaf902ae9ac6d9"
    DEEPSEEK_API_KEY: Optional[str] = "sk-197d6e94cdb643609583f5e73ba1719b"
    
    # File paths
    DATA_DIR: str = "./data"
    LOGS_DIR: str = "./logs"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Ensure data directories exist
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.LOGS_DIR, exist_ok=True)
