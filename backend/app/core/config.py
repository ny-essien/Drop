from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()

class Settings(BaseSettings):
    # MongoDB settings
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "dropshipping"
    
    # JWT settings
    JWT_SECRET: str = "your-secret-key-here"  # Change this in production
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"
    
    # Stripe settings
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # AWS settings
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: Optional[str] = None
    
    # CORS settings
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000"]
    
    # Server settings
    PORT: str = "5000"
    FRONTEND_URL: str = "http://localhost:3000"

    # SMTP settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: str = "587"
    SMTP_SECURE: str = "false"
    SMTP_USER: Optional[str] = None
    SMTP_PASS: Optional[str] = None
    SMTP_FROM: Optional[str] = None

    # PostgreSQL settings
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "dropshipping"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields in the environment

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings() 