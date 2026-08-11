from pydantic import BaseModel

class Chunk(BaseModel):
    content: str
    metadata: dict