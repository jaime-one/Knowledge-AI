from unittest.mock import MagicMock, patch
from langchain_core.messages import AIMessage
from langchain_core.runnables import Runnable

from app.models.knowledge_worker import KnowledgeOutput
from app.models.classification_worker import ClassificationOutput
from app.models.markdown_worker import MarkdownOutput
from app.models.retrieval_worker import RetrievalMatch
from app.models.decision_worker import DecisionOutput
from app.workers.decision_worker import run_decision_worker


def test_run_decision_worker_new_note_calls_tools_in_order():
    fake_knowledge = KnowledgeOutput(
        title="Tipos de corriente eléctrica",
        summary="Diferencias entre corriente continua y corriente alterna.",
        key_concepts=["corriente continua", "corriente alterna"],
        content="Contenido de prueba",
        corrections=[],
    )
    fake_retrieval = []  # sin notas relacionadas: es contenido nuevo
    fake_classification = ClassificationOutput(folder_path="electricidad", is_new_folder=True)
    fake_markdown = MarkdownOutput(filename="tipos-de-corriente-electrica.md", content="---\n---\ncontenido")
    fake_decision = DecisionOutput(
        action="nueva",
        target_path="electricidad/tipos-de-corriente-electrica.md",
        content=fake_markdown.content,
    )

    # El modelo pide, en orden: retrieval -> classification -> markdown -> termina
    tool_call_responses = [
        AIMessage(content="", tool_calls=[
            {"name": "retrieval_tool", "args": {"query": "corriente eléctrica"}, "id": "call_1"},
        ]),
        AIMessage(content="", tool_calls=[
            {"name": "classification_tool", "args": {}, "id": "call_2"},
        ]),
        AIMessage(content="", tool_calls=[
            {"name": "markdown_tool", "args": {}, "id": "call_3"},
        ]),
        AIMessage(content="Listo, decidí que es una nota nueva.", tool_calls=[]),
    ]

    with patch("app.workers.decision_worker.get_llm") as mock_get_llm, \
         patch("app.workers.decision_worker.run_retrieval_worker") as mock_retrieval, \
         patch("app.workers.decision_worker.run_classification_worker") as mock_classification, \
         patch("app.workers.decision_worker.run_markdown_worker") as mock_markdown:

        mock_retrieval.return_value = fake_retrieval
        mock_classification.return_value = fake_classification
        mock_markdown.return_value = fake_markdown

        mock_llm_with_tools = MagicMock(spec=Runnable)
        mock_llm_with_tools.invoke.side_effect = tool_call_responses

        mock_structured_llm = MagicMock(spec=Runnable)
        mock_structured_llm.invoke.return_value = fake_decision

        mock_get_llm.return_value.bind_tools.return_value = mock_llm_with_tools
        mock_get_llm.return_value.with_structured_output.return_value = mock_structured_llm

        result = run_decision_worker(fake_knowledge, existing_folders=["astronomia/galaxias"])

    assert result == fake_decision
    mock_retrieval.assert_called_once()
    mock_classification.assert_called_once_with(fake_knowledge, ["astronomia/galaxias"])
    mock_markdown.assert_called_once_with(fake_knowledge)
    assert mock_llm_with_tools.invoke.call_count == 4
