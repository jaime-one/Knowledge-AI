from pathlib import Path

from app.config.settings import settings
from app.models.decision_worker import DecisionOutput
from app.models.markdown_worker import MarkdownOutput
from app.workers.chunk_worker import run_chunk_worker
from app.workers.embedding_worker import run_embedding_worker
from app.services.chroma_client import get_collection


def run_save_worker(decision: DecisionOutput) -> None:
    note_path = Path(settings.vault_path) / decision.target_path
    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text(decision.content, encoding="utf-8")

    if decision.action != "nueva":
        collection = get_collection()
        collection.delete(where={"source": decision.old_path})

        if decision.old_path != decision.target_path:
            old_note_path = Path(settings.vault_path) / decision.old_path
            old_note_path.unlink(missing_ok=True)

    markdown = MarkdownOutput(filename=decision.target_path, content=decision.content)
    chunks = run_chunk_worker(markdown)
    run_embedding_worker(chunks)
