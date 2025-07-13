from dotenv import load_dotenv
load_dotenv()

from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from urllib.parse import urlparse

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Database - Railway provides DATABASE_URL automatically
    DATABASE_URL: Optional[str] = "postgresql+asyncpg://postgres:stocksight1484@100.75.201.24:5432/TAIFA_db"
    
    # Parse database URL for individual components (if needed)
    @property
    def database_components(self):
        if self.DATABASE_URL:
            parsed = urlparse(self.DATABASE_URL)
            return {
                "host": parsed.hostname,
                "port": parsed.port,
                "database": parsed.path.lstrip('/'),
                "username": parsed.username,
                "password": parsed.password
            }
        return {}
    
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
    
    # Railway-specific settings
    RAILWAY_DEPLOYMENT_ID: Optional[str] = None
    RAILWAY_ENVIRONMENT_NAME: Optional[str] = None
    RAILWAY_SERVICE_NAME: Optional[str] = None
    
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
            
            # Add Railway app domains
            if self.RAILWAY_SERVICE_NAME:
                origins.extend([
                    f"https://{self.RAILWAY_SERVICE_NAME}.up.railway.app",
                    "https://*.up.railway.app"
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
    SERPER_DEV_API_KEY: Optional[str] = None
    DEEPL_API_KEY: Optional[str] = None
    AZURE_TRANSLATOR_KEY: Optional[str] = None
    AZURE_TRANSLATOR_REGION: Optional[str] = None
    GOOGLE_TRANSLATE_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    # Webhook URLs
    N8N_WEBHOOK_URL: Optional[str] = None
    SLACK_WEBHOOK_URL: Optional[str] = None
    DISCORD_WEBHOOK_URL: Optional[str] = None
    
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
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Ensure data directories exist
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.LOGS_DIR, exist_ok=True)

# Validation for production
if settings.ENVIRONMENT == "production":
    required_vars = ["DATABASE_URL", "SECRET_KEY"]
    missing_vars = [var for var in required_vars if not getattr(settings, var, None)]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables for production: {missing_vars}")
    
    # Warn about missing optional but recommended vars
    recommended_vars = ["SERPER_DEV_API_KEY", "OPENAI_API_KEY"]
    missing_recommended = [var for var in recommended_vars if not getattr(settings, var, None)]
    
    if missing_recommended:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Missing recommended environment variables: {missing_recommended}")

