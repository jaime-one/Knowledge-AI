import hashlib

from app.models.chunk_worker import Chunk
from app.services.llm_factory import get_embedder
from app.services.chroma_client import get_collection


def _make_chunk_id(chunk: Chunk) -> str:
    raw = f"{chunk.metadata['source']}::{chunk.content}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def run_embedding_worker(chunks: list[Chunk]) -> list[str]:
    collection = get_collection()

    embedder = get_embedder("embedding_worker")
    ids = [_make_chunk_id(chunk) for chunk in chunks]
    embeddings = embedder.embed_documents([chunk.content for chunk in chunks])

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=[chunk.content for chunk in chunks],
        metadatas=[chunk.metadata for chunk in chunks],
    )
    return ids