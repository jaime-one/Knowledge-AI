from pathlib import Path
import yaml
from pydantic import BaseModel

class WorkerModelConfig(BaseModel):
    provider: str
    model: str
    temperature: float

class EmbeddingModelConfig(BaseModel):
    provider: str
    model: str

class ModelsConfig(BaseModel):
    knowledge_worker: WorkerModelConfig
    classification_worker: WorkerModelConfig
    decision_worker: WorkerModelConfig
    markdown_worker: WorkerModelConfig
    embedding_worker: EmbeddingModelConfig

def load_models_config() -> ModelsConfig:
    path = Path(__file__).parent / "models.yaml"
    with open(path) as f:
        data = yaml.safe_load(f)
    return ModelsConfig(**data)

models_config = load_models_config()