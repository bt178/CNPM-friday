from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )
    
    # Project
    PROJECT_NAME: str = "CollabSphere API"
    API_V1_STR: str = "/api/v1"
    
    # Database
    # SỬA LỖI: Thêm +asyncpg để chạy async SQLAlchemy
    DATABASE_URL: str = "postgresql+asyncpg://collabsphere:collabsphere_password@localhost:5432/collabsphere_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS - can be set as comma-separated string in env
    # SỬA LỖI: Thêm * để linh hoạt khi test máy khác, hoặc liệt kê IP cụ thể
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,*"
    
    # Google Gemini API
    GOOGLE_GEMINI_API_KEY: str = ""
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS_ORIGINS string to list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    @property
    def BACKEND_CORS_ORIGINS(self) -> List[str]:
        """Alias for cors_origins_list for backward compatibility."""
        return self.cors_origins_list


# Create a single instance of Settings
settings = Settings()

