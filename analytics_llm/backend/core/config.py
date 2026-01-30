"""
Enterprise configuration with environment-based settings
Supports development, staging, and production environments
"""
import os
from typing import List
from functools import lru_cache

class Settings:
    """Application settings loaded from environment variables"""
    
    # Environment
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Security
    JWT_SECRET: str = os.getenv("JWT_SECRET", "CHANGE_ME_IN_PRODUCTION")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_TTL_MIN: int = int(os.getenv("ACCESS_TOKEN_TTL_MIN", "60"))
    REFRESH_TOKEN_TTL_DAYS: int = int(os.getenv("REFRESH_TOKEN_TTL_DAYS", "7"))
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./analytics.db" # Fallback to SQLite for easy start
    )
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    
    # Redis Cache
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_TTL_SECONDS: int = int(os.getenv("REDIS_TTL_SECONDS", "3600"))
    
    # Vector Store
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "/tmp/vectors")
    VECTOR_DB_PROVIDER: str = os.getenv("VECTOR_DB_PROVIDER", "chromadb")
    
    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE: int = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "100"))
    MAX_LOGIN_ATTEMPTS: int = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
    
    # LLM Configuration
    MAX_TOKENS_PER_MIN: int = int(os.getenv("MAX_TOKENS_PER_MIN", "50000"))
    LLM_TIMEOUT_SECONDS: int = int(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
    LLM_MAX_RETRIES: int = int(os.getenv("LLM_MAX_RETRIES", "3"))
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
    
    # Gemini/Gemma
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMMA_MODEL: str = os.getenv("GEMMA_MODEL", "gemma-2-9b-it")
    
    # Observability
    ENABLE_TELEMETRY: bool = os.getenv("ENABLE_TELEMETRY", "true").lower() == "true"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:8501,https://*.streamlit.app"
    ).split(",")
    
    # API Settings
    API_VERSION: str = "v1"
    API_PREFIX: str = f"/api/{API_VERSION}"
    
    # File Upload
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "100"))
    ALLOWED_FILE_TYPES: List[str] = ["csv", "json", "parquet", "xlsx"]
    
    # Session Management
    SESSION_TTL_HOURS: int = int(os.getenv("SESSION_TTL_HOURS", "24"))
    MAX_SESSIONS_PER_USER: int = int(os.getenv("MAX_SESSIONS_PER_USER", "10"))
    
    # Deployment
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    WORKERS: int = int(os.getenv("WORKERS", "4"))
    
    # Streamlit Configuration
    STREAMLIT_SERVER_PORT: int = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
    STREAMLIT_SERVER_ADDRESS: str = os.getenv("STREAMLIT_SERVER_ADDRESS", "0.0.0.0")
    
    # API URL for Streamlit frontend
    API_URL: str = os.getenv("API_URL", "http://api:8000")
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENV == "production"
    
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENV == "development"
    
    def validate(self):
        """Validate critical settings"""
        errors = []
        
        if self.is_production():
            if self.JWT_SECRET == "CHANGE_ME_IN_PRODUCTION":
                errors.append("JWT_SECRET must be set in production")
            
            if not self.OPENAI_API_KEY and not self.GEMINI_API_KEY:
                errors.append("At least one LLM API key must be set")
            
            if not self.DATABASE_URL or "localhost" in self.DATABASE_URL:
                errors.append("DATABASE_URL must be set for production")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    settings = Settings()
    settings.validate()
    return settings

# Global settings instance
settings = get_settings()
