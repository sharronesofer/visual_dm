from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List, Optional, Union, Dict, Any
import secrets
from pydantic import validator, field_validator, Field

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Visual DM"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    @field_validator("BACKEND_CORS_ORIGINS")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    ASYNC_SQLALCHEMY_DATABASE_URI: Optional[str] = None
    
    # Redis (for rate limiting and caching)
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[int] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )

settings = Settings() 