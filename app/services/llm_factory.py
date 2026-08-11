from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings


from app.config.settings import settings
from app.config.model_config import models_config


def get_llm(worker_name: str) -> BaseChatModel:
    config = getattr(models_config, worker_name, None)
    if config is None:
        raise ValueError(f"No hay configuración de modelo para el worker '{worker_name}'")

    if config.provider == "openai":
        llm = ChatOpenAI(
            model=config.model,
            temperature=config.temperature,
            api_key=settings.gpt_api_key,
            )
        return llm

    elif config.provider == "anthropic":
        llm = ChatAnthropic(
            model=config.model,
            temperature=config.temperature,
            api_key=settings.anthropic_api_key,
            )    
        return llm
   
    else:
        raise ValueError(f"Proveedor desconocido: {config.provider}")


def get_embedder(worker_name: str) -> Embeddings:
    config = getattr(models_config, worker_name, None)
    if config is None:
        raise ValueError(f"No hay configuración de modelo para el worker '{worker_name}'")

    if config.provider == "openai":
        return OpenAIEmbeddings(
            model=config.model,
            api_key=settings.gpt_api_key,
        )
    else:
        raise ValueError(f"Proveedor desconocido: {config.provider}")