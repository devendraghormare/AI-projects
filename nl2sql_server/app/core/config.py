from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import ClassVar

class Settings(BaseSettings):
    DATABASE_URL: str
    OPENAI_API_KEY: str

    # Correct attribute name is 'model_config', not 'config'
    model_config: ClassVar[ConfigDict] = ConfigDict(env_file=".env")

settings = Settings()
