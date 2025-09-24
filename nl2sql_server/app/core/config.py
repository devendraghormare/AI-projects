from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import ClassVar

class Settings(BaseSettings):
    DATABASE_URL: str
    OPENAI_API_KEY: str
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

    model_config: ClassVar[ConfigDict] = ConfigDict(env_file=".env")

settings = Settings()
