import os

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    anthropic_api_key: str #Si no está en .env error al arrancar. Sin default.
    gpt_api_key: str
    debug: bool = False #Si DEBUG no existe en .env, usa False
    vault_path: str

    langsmith_tracing: bool = False
    langsmith_endpoint: str = ""
    langsmith_api_key: str = ""
    langsmith_project: str = ""

settings = Settings()

# LangChain/LangGraph leen estas variables directo de os.environ, no de
# nuestro Settings — .env solo lo lee pydantic-settings para llenar Settings,
# así que hay que empujarlas a mano para que la traza de LangSmith se active.
if settings.langsmith_tracing:
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_ENDPOINT"] = settings.langsmith_endpoint
    os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
    os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project