from app.models.retrieval_worker import RetrievalMatch
from app.services.llm_factory import get_embedder
from app.services.chroma_client import get_collection


def run_retrieval_worker(query_text: str, n_results: int = 5) -> list[RetrievalMatch]:
    collection = get_collection()
    embedder = get_embedder("embedding_worker")

    query_embedding = embedder.embed_query(query_text)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )

    # results = {
    #     "documents": [ ["doc A", "doc B", "doc C"] ],   # 1 lista adentro de otra lista
    #     "metadatas": [ [ {...}, {...}, {...} ] ],
    #     "distances": [ [ 0.12, 0.34, 0.56 ] ],
    # }

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    return [
        RetrievalMatch(content=doc, metadata=meta, distance=dist)
        for doc, meta, dist in zip(documents, metadatas, distances)
    ]
