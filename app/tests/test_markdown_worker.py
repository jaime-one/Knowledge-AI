from app.models.knowledge_worker import KnowledgeOutput
from app.workers.markdown_worker import run_markdown_worker


def test_run_markdown_worker_builds_filename_and_frontmatter():
    knowledge = KnowledgeOutput(
        title="Mi Primera Nota",
        summary="resumen",
        key_concepts=["A", "B"],
        content="cuerpo de la nota",
        corrections=[],
    )

    result = run_markdown_worker(knowledge)

    assert result.filename == "mi-primera-nota.md"
    assert "title: Mi Primera Nota" in result.content
    assert "# Mi Primera Nota" in result.content
    assert "cuerpo de la nota" in result.content
