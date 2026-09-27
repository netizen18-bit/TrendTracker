import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "ContentPulse"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite+aiosqlite:///./contentpulse.db"
    )
    
    # Monitoring Defaults
    DEFAULT_CHECK_INTERVAL_SEC: int = 60
    MAX_CONCURRENT_WORKERS: int = 25
    REQUEST_TIMEOUT_SECONDS: float = 10.0
    USER_AGENT: str = "ContentPulse-Monitor/1.0 (+https://contentpulse.local/bot; Real-Time Content Intelligence)"
    
    # SLA Target in seconds (5 minutes = 300s)
    SLA_TARGET_SECONDS: int = 300
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    model_config = SettingsConfigDict(case_sensitive=True)

settings = Settings()
