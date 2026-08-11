from unittest.mock import patch

from app.models.knowledge_worker import KnowledgeOutput
from app.models.decision_worker import DecisionOutput
from app.graph.ingestion_graph import run_ingestion_graph


def test_run_ingestion_graph_wires_knowledge_into_decision():
    fake_knowledge = KnowledgeOutput(
        title="Tipos de corriente eléctrica",
        summary="Diferencias entre corriente continua y corriente alterna.",
        key_concepts=["corriente continua", "corriente alterna"],
        content="Contenido de prueba",
        corrections=[],
    )
    fake_decision = DecisionOutput(
        action="nueva",
        target_path="electricidad/tipos-de-corriente-electrica.md",
        content="contenido final",
    )

    with patch("app.graph.ingestion_graph.run_knowledge_worker") as mock_knowledge, \
         patch("app.graph.ingestion_graph.run_decision_worker") as mock_decision, \
         patch("app.graph.ingestion_graph.list_existing_folders") as mock_list_folders:

        mock_knowledge.return_value = fake_knowledge
        mock_list_folders.return_value = ["astronomia/galaxias"]
        mock_decision.return_value = fake_decision

        result = run_ingestion_graph("texto crudo de prueba")

    assert result == (fake_knowledge, fake_decision)
    mock_knowledge.assert_called_once_with(
        "texto crudo de prueba", main_theme=None, context=None
    )
    mock_decision.assert_called_once_with(fake_knowledge, ["astronomia/galaxias"])


def test_run_ingestion_graph_passes_main_theme_and_context_through():
    fake_knowledge = KnowledgeOutput(
        title="Tipos de corriente eléctrica",
        summary="Diferencias entre corriente continua y corriente alterna.",
        key_concepts=["corriente continua", "corriente alterna"],
        content="Contenido de prueba",
        corrections=[],
    )
    fake_decision = DecisionOutput(
        action="nueva",
        target_path="electricidad/tipos-de-corriente-electrica.md",
        content="contenido final",
    )

    with patch("app.graph.ingestion_graph.run_knowledge_worker") as mock_knowledge, \
         patch("app.graph.ingestion_graph.run_decision_worker") as mock_decision, \
         patch("app.graph.ingestion_graph.list_existing_folders") as mock_list_folders:

        mock_knowledge.return_value = fake_knowledge
        mock_list_folders.return_value = ["astronomia/galaxias"]
        mock_decision.return_value = fake_decision

        run_ingestion_graph(
            "texto crudo de prueba",
            main_theme="avalanchas",
            context="curso de montañismo",
        )

    mock_knowledge.assert_called_once_with(
        "texto crudo de prueba",
        main_theme="avalanchas",
        context="curso de montañismo",
    )
