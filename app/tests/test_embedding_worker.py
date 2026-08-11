from unittest.mock import MagicMock, patch

from app.models.chunk_worker import Chunk
from app.workers.embedding_worker import run_embedding_worker


def test_run_embedding_worker_adds_chunks():
    chunks = [
        Chunk(content="contenido uno", metadata={"source": "nota.md", "header_2": "Tema uno"}),
        Chunk(content="contenido dos", metadata={"source": "nota.md", "header_2": "Tema dos"}),
    ]

    with patch("app.workers.embedding_worker.get_collection") as mock_get_collection, \
         patch("app.workers.embedding_worker.get_embedder") as mock_get_embedder:

        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        mock_get_embedder.return_value.embed_documents.return_value = [[0.1, 0.2], [0.3, 0.4]]

        result = run_embedding_worker(chunks)

    mock_collection.delete.assert_not_called()
    mock_collection.add.assert_called_once()
    assert len(result) == 2