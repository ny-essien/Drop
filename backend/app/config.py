from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/dropshipping"
    
    # JWT settings
    JWT_SECRET_KEY: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    # Notification settings
    NOTIFICATION_QUEUE_SIZE: int = 1000
    NOTIFICATION_RETRY_ATTEMPTS: int = 3
    
    class Config:
        env_file = ".env"

settings = Settings() 