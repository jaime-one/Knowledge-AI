from pydantic import BaseModel

class MarkdownOutput(BaseModel):
    filename: str
    content: str