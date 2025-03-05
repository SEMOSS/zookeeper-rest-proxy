import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Server settings
    HOST: str = os.environ.get("HOST", "0.0.0.0")
    PORT: int = int(os.environ.get("PORT", "8000"))
    DEBUG: bool = os.environ.get("DEBUG", "False").lower() == "true"

    # ZooKeeper settings
    ZK_HOSTS: str = os.environ.get("ZK_HOSTS", "localhost:2181")
    ZK_TIMEOUT: float = float(os.environ.get("ZK_TIMEOUT", "10.0"))
    ZK_READ_ONLY: bool = os.environ.get("ZK_READ_ONLY", "True").lower() == "true"

    # Security settings
    API_KEY_ENABLED: bool = os.environ.get("API_KEY_ENABLED", "False").lower() == "true"
    API_KEY: str = os.environ.get("API_KEY", "")

    # CORS settings
    CORS_ORIGINS: List[str] = [
        origin.strip() for origin in os.environ.get("CORS_ORIGINS", "*").split(",")
    ]

    class Config:
        """Pydantic config"""

        env_file = ".env"
        case_sensitive = True


settings = Settings()
