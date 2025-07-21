from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from urllib.parse import urlparse
from dotenv import load_dotenv
from pathlib import Path

# Load .env file from the project root
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / '.env')

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    
    # Redis (optional for Railway)
    REDIS_URL: Optional[str] = None
    
    # API Configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    API_V1_STR: str = "/api/v1"
    
    # Environment Detection
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    
    # CORS Configuration - Production-ready
    @property
    def BACKEND_CORS_ORIGINS(self) -> List[str]:
        origins = []
        
        # Add environment-specific origins
        if self.ENVIRONMENT == "production":
            origins.extend([
                "https://taifa-africa.com",
                "https://fiala-afrique.com", 
                "https://taifa-fiala.net",
                "https://www.taifa-africa.com",
                "https://www.fiala-afrique.com",
                "https://api.taifa-fiala.net"
            ])
        
        else:
            # Development origins
            origins.extend([
                "http://localhost:3000",
                "http://localhost:8501", 
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8501"
            ])
        
        # Allow custom origins from environment
        custom_origins = os.getenv("BACKEND_CORS_ORIGINS")
        if custom_origins:
            try:
                import json
                origins.extend(json.loads(custom_origins))
            except:
                origins.extend(custom_origins.split(","))
        
        return origins
    
    # Data Collection Configuration
    RSS_CHECK_INTERVAL_MINUTES: int = 360  # 6 hours for production
    SCRAPING_DELAY_SECONDS: int = 2
    MAX_CONCURRENT_REQUESTS: int = 3  # Lower for production
    USER_AGENT: str = "TAIFA-Production/1.0"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    RATE_LIMIT_REQUESTS_PER_HOUR: int = 1000
    
    # Email Configuration
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # External APIs
    OPENAI_API_KEY: Optional[str] = None
    SERPER_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    # Database connection
    DB_USER: Optional[str] = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: Optional[str] = os.getenv("DB_PASSWORD")
    DB_HOST: Optional[str] = os.getenv("DB_HOST")
    DB_PORT: Optional[int] = os.getenv("DB_PORT", 5432)
    DB_NAME: Optional[str] = os.getenv("DB_NAME", "postgres")

    # Supabase Configuration
    SUPABASE_URL: Optional[str] = None
    SUPABASE_API_KEY: Optional[str] = None
    SUPABASE_PUBLISHABLE_KEY: Optional[str] = None
    SUPABASE_JWT_SECRET: Optional[str] = None
    SUPABASE_PROJECT_ID: Optional[str] = None

    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL for SQLAlchemy"""
        if all([self.DB_USER, self.DB_PASSWORD, self.DB_HOST, self.DB_PORT, self.DB_NAME]):
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return "sqlite:///./test.db"  # Fallback for local dev

    # Pinecone Configuration
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_INDEX_NAME: Optional[str] = None
    PINECONE_HOST: Optional[str] = None
    
    # Webhook URLs
    N8N_WEBHOOK_URL: Optional[str] = None
    
    # Feature Flags
    ENABLE_TRANSLATION_QUEUE: bool = True
    ENABLE_BILINGUAL_ROUTING: bool = True
    ENABLE_DATA_COLLECTION: bool = True
    ENABLE_COMMUNITY_SUBMISSIONS: bool = True
    
    # Security Settings
    @property
    def ALLOWED_HOSTS(self) -> List[str]:
        hosts = []
        
        if self.ENVIRONMENT == "production":
            hosts.extend([
                "taifa-africa.com",
                "fiala-afrique.com",
                "api.taifa-fiala.net",
                "*.up.railway.app"
            ])
        else:
            hosts.extend(["localhost", "127.0.0.1"])
        
        # Add custom hosts from environment
        custom_hosts = os.getenv("ALLOWED_HOSTS")
        if custom_hosts:
            try:
                import json
                hosts.extend(json.loads(custom_hosts))
            except:
                hosts.extend(custom_hosts.split(","))
        
        return hosts
    
    # File paths - Railway-compatible
    @property
    def DATA_DIR(self) -> str:
        if self.ENVIRONMENT == "production":
            return "/tmp/taifa_data"  # Railway uses /tmp for writable storage
        return "./data"
    
    @property 
    def LOGS_DIR(self) -> str:
        if self.ENVIRONMENT == "production":
            return "/tmp/taifa_logs"
        return "./logs"
    
    class Config:
        case_sensitive = True
        extra = "ignore"


settings = Settings()
