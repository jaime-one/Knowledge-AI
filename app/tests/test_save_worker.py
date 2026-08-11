from unittest.mock import patch

from app.models.decision_worker import DecisionOutput
from app.models.chunk_worker import Chunk
from app.workers.save_worker import run_save_worker
from app.config.settings import settings


def test_run_save_worker_new_note_writes_file_and_skips_delete(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "vault_path", str(tmp_path))
    decision = DecisionOutput(action="nueva", target_path="electricidad/nota.md", content="contenido nuevo")
    fake_chunks = [Chunk(content="c1", metadata={"source": "electricidad/nota.md"})]

    with patch("app.workers.save_worker.run_chunk_worker") as mock_chunk, \
         patch("app.workers.save_worker.run_embedding_worker") as mock_embed, \
         patch("app.workers.save_worker.get_collection") as mock_get_collection:

        mock_chunk.return_value = fake_chunks

        run_save_worker(decision)

    saved_path = tmp_path / "electricidad" / "nota.md"
    assert saved_path.read_text(encoding="utf-8") == "contenido nuevo"
    mock_get_collection.return_value.delete.assert_not_called()
    mock_chunk.assert_called_once()
    mock_embed.assert_called_once_with(fake_chunks)


def test_run_save_worker_edit_deletes_old_chunks_first(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "vault_path", str(tmp_path))
    note_dir = tmp_path / "electricidad"
    note_dir.mkdir()
    (note_dir / "nota.md").write_text("contenido viejo")

    decision = DecisionOutput(
        action="editar",
        target_path="electricidad/nota.md",
        old_path="electricidad/nota.md",
        content="contenido fusionado",
    )

    with patch("app.workers.save_worker.run_chunk_worker") as mock_chunk, \
         patch("app.workers.save_worker.run_embedding_worker"), \
         patch("app.workers.save_worker.get_collection") as mock_get_collection:

        mock_chunk.return_value = []

        run_save_worker(decision)

    saved_path = note_dir / "nota.md"
    assert saved_path.read_text(encoding="utf-8") == "contenido fusionado"
    mock_get_collection.return_value.delete.assert_called_once_with(where={"source": "electricidad/nota.md"})


def test_run_save_worker_rename_writes_new_file_deletes_old_file_and_old_chunks(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "vault_path", str(tmp_path))
    note_dir = tmp_path / "nieve"
    note_dir.mkdir()
    (note_dir / "zapatos-nieve.md").write_text("contenido viejo")

    decision = DecisionOutput(
        action="agregar",
        target_path="nieve/articulos-nieve.md",
        old_path="nieve/zapatos-nieve.md",
        content="contenido fusionado",
    )

    with patch("app.workers.save_worker.run_chunk_worker") as mock_chunk, \
         patch("app.workers.save_worker.run_embedding_worker"), \
         patch("app.workers.save_worker.get_collection") as mock_get_collection:

        mock_chunk.return_value = []

        run_save_worker(decision)

    assert (note_dir / "articulos-nieve.md").read_text(encoding="utf-8") == "contenido fusionado"
    assert not (note_dir / "zapatos-nieve.md").exists()
    mock_get_collection.return_value.delete.assert_called_once_with(where={"source": "nieve/zapatos-nieve.md"})
