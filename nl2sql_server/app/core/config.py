from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import ClassVar

class Settings(BaseSettings):
    DATABASE_URL: str
    OPENAI_API_KEY: str

    # Annotate 'config' as a ClassVar to avoid errors
    config: ClassVar[ConfigDict] = ConfigDict(env_file=".env")

settings = Settings()
