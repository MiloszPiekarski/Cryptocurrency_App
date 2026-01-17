"""
TURBO-PLAN X - Backend API Configuration
Centralized settings management
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os
from pydantic import Field

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "TURBO-PLAN X API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENV: str = "development"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database - Google Cloud SQL (Hot Storage) - FORCE CLOUD
    # We use validation_alias to ignore 'DATABASE_URL' from .env and force the default (Cloud)
    # MODIFICATION: Now strictly reading from env or falling back to constructed URL from components
    DATABASE_URL: str = Field(
        default_factory=lambda: os.getenv("CLOUD_SQL_URL"),
        validation_alias="CLOUD_SQL_URL" 
    )
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DECODE_RESPONSES: bool = True
    
    # CORS
    FRONTEND_URL: str = "http://localhost:3000"
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:3001"]
    
    # Exchange APIs
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_SECRET: Optional[str] = None
    BYBIT_API_KEY: Optional[str] = None
    BYBIT_SECRET: Optional[str] = None
    
    # AI/ML
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # SMTP
    SMTP_EMAIL: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Dependency for FastAPI to inject settings"""
    return settings
