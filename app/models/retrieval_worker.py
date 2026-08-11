from pydantic import BaseModel

class RetrievalMatch(BaseModel):
    content: str
    metadata: dict
    distance: float