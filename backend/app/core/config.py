from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # Project setup
    PROJECT_NAME: str = "AI_KNOWLEDGEBASE_APP"
    DEBUG: bool = False

    # Database setup
    DATABASE_URL: str

    # Auth Variables
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # LLM setup
    OPENAI_API_KEY: str
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Knowledge base tuning
    VECTOR_DIMENSION: int = 1536
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 150
    TOP_K_MATCHES: int = 4
    MAX_CONTEXT_CHARS: int = 8000

    # CORS (comma-separated via env is supported by pydantic-settings as JSON.
    # Keeping defaults simple for local development.)
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    ENVIRONMENT: str = Field(default="local")

settings = Settings()
