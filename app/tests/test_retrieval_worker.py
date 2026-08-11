from unittest.mock import MagicMock, patch

from app.workers.retrieval_worker import run_retrieval_worker


def test_run_retrieval_worker_returns_matches():
    fake_results = {
        "documents": [["doc A", "doc B"]],
        "metadatas": [[{"source": "a.md"}, {"source": "b.md"}]],
        "distances": [[0.1, 0.3]],
    }

    with patch("app.workers.retrieval_worker.get_collection") as mock_get_collection, \
         patch("app.workers.retrieval_worker.get_embedder") as mock_get_embedder:

        mock_collection = MagicMock()
        mock_collection.query.return_value = fake_results
        mock_get_collection.return_value = mock_collection
        mock_get_embedder.return_value.embed_query.return_value = [0.1, 0.2, 0.3]

        result = run_retrieval_worker("texto de consulta", n_results=2)

    mock_get_embedder.return_value.embed_query.assert_called_once_with("texto de consulta")
    mock_collection.query.assert_called_once_with(query_embeddings=[[0.1, 0.2, 0.3]], n_results=2)
    assert len(result) == 2
    assert result[0].content == "doc A"
    assert result[0].distance == 0.1
    assert result[0].metadata == {"source": "a.md"}
