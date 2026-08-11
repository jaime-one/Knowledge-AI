from pathlib import Path
import chromadb

CHROMA_PATH = Path(__file__).parent.parent.parent / "chroma"

def get_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    return client.get_or_create_collection(
        name="knowledge",
        metadata={"hnsw:space": "cosine"},
    )
