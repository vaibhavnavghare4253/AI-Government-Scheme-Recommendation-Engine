from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Government Scheme Recommendation Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/schemes_db"
    
    # AWS
    AWS_REGION: str = "ap-south-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    
    # S3
    S3_BUCKET_DOCUMENTS: str = "scheme-documents"
    S3_BUCKET_ASSETS: str = "scheme-assets"
    
    # Cognito
    COGNITO_USER_POOL_ID: str = ""
    COGNITO_CLIENT_ID: str = ""
    COGNITO_REGION: str = "ap-south-1"
    
    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # AI Services
    BEDROCK_MODEL_ID: str = "anthropic.claude-v2"
    OPENAI_API_KEY: str = ""
    
    # DynamoDB
    DYNAMODB_SESSIONS_TABLE: str = "user-sessions"
    DYNAMODB_CACHE_TABLE: str = "scheme-cache"
    
    # OpenSearch
    OPENSEARCH_ENDPOINT: str = ""
    OPENSEARCH_INDEX: str = "schemes"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
