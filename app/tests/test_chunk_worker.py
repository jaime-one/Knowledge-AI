# app/tests/test_chunk_worker.py
from app.models.markdown_worker import MarkdownOutput
from app.workers.chunk_worker import run_chunk_worker


def test_run_chunk_worker_splits_by_headers():
    markdown = MarkdownOutput(
        filename="test.md",
        content="""---
title: Prueba
created: 2026-07-26
concepts: a, b
---

## Tema uno
Contenido del primer tema.

## Tema dos
Contenido del segundo tema.
""",
    )

    chunks = run_chunk_worker(markdown)

    assert len(chunks) == 2
    assert chunks[0].metadata["header_2"] == "Tema uno"
    assert chunks[1].metadata["header_2"] == "Tema dos"
    assert chunks[0].metadata["source"] == "test.md"
    assert chunks[0].metadata["title"] == "Prueba"