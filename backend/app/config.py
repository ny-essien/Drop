from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Server settings
    port: int = 5000
    
    # Database settings
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "dropshipping"
    
    # PostgreSQL settings
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "dropshipping"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    
    # Redis settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    
    # JWT and security settings
    jwt_secret: str = "your-secret-key-here"
    secret_key: str = "your-secret-key-here"
    
    # Frontend settings
    frontend_url: str = "http://localhost:3000"
    
    # Email settings
    smtp_secure: bool = False
    smtp_pass: str = "your-app-password"
    smtp_from: str = "your-email@gmail.com"
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    
    # Notification settings
    NOTIFICATION_QUEUE_SIZE: int = 1000
    NOTIFICATION_RETRY_ATTEMPTS: int = 3
    
    # Stripe settings
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    
    class Config:
        env_file = ".env"
        extra = "allow"  # This will allow extra fields in the environment

settings = Settings() 