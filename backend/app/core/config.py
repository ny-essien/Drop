from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings
from typing import Optional, List
from pathlib import Path
import os
from dotenv import load_dotenv
from functools import lru_cache
from pydantic import validator

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Dropshipping Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-here"  # Change in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    # Database Configuration
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "dropshipping"
    
    # JWT Configuration
    JWT_SECRET_KEY: str = "your-jwt-secret-key"  # Change in production
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email Configuration
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: Optional[str] = None
    S3_BUCKET: Optional[str] = None
    
    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"
    
    # Stripe settings
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # Server settings
    PORT: str = "5000"
    FRONTEND_URL: str = "http://localhost:3000"

    # PostgreSQL settings
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "dropshipping"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: Optional[str] = None

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields in the environment

    @property
    def BASE_PATH(self) -> Path:
        return Path(__file__).resolve().parent.parent

    def assemble_cors_origins(self) -> List[str]:
        cors_origins = []
        if self.BACKEND_CORS_ORIGINS:
            cors_origins.extend(
                origin.strip() for origin in self.BACKEND_CORS_ORIGINS
            )
        return cors_origins

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings() 