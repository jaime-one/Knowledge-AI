from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api.main import app
from app.models.knowledge_worker import ConceptCorrection, KnowledgeOutput
from app.models.decision_worker import DecisionOutput
from app.services.proposal_store import PendingProposal

client = TestClient(app)


def _fake_knowledge(corrections: list[ConceptCorrection] | None = None) -> KnowledgeOutput:
    return KnowledgeOutput(
        title="Tipos de corriente eléctrica",
        summary="Diferencias entre corriente continua y corriente alterna.",
        key_concepts=["corriente continua", "corriente alterna"],
        content="Contenido de prueba",
        corrections=corrections or [],
    )


def _fake_decision() -> DecisionOutput:
    return DecisionOutput(
        action="nueva",
        target_path="electricidad/tipos-de-corriente-electrica.md",
        content="contenido final",
    )


def test_create_proposal_returns_proposal_response():
    fake_knowledge = _fake_knowledge(
        corrections=[
            ConceptCorrection(
                concept="corriente alterna",
                user_understanding="siempre va en una sola dirección",
                correct_explanation="la corriente alterna invierte periódicamente su dirección",
            )
        ]
    )
    fake_decision = _fake_decision()

    with patch("app.api.proposals_routes.run_ingestion_graph") as mock_graph, \
         patch("app.api.proposals_routes.save_proposal") as mock_save:
        mock_graph.return_value = (fake_knowledge, fake_decision)
        mock_save.return_value = "abc-123"

        response = client.post(
            "/api/proposals",
            json={"text": "nota cruda", "main_theme": "electricidad", "context": None},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["proposal_id"] == "abc-123"
    assert body["decision"]["target_path"] == fake_decision.target_path
    assert len(body["corrections"]) == 1
    mock_graph.assert_called_once_with("nota cruda", main_theme="electricidad", context=None)
    mock_save.assert_called_once_with(fake_knowledge, fake_decision)


def test_create_proposal_returns_500_on_pipeline_failure():
    with patch("app.api.proposals_routes.run_ingestion_graph") as mock_graph:
        mock_graph.side_effect = RuntimeError("el LLM explotó")

        response = client.post("/api/proposals", json={"text": "nota cruda"})

    assert response.status_code == 500


def test_create_proposal_rejects_empty_text():
    response = client.post("/api/proposals", json={"text": ""})

    assert response.status_code == 422


def test_approve_proposal_runs_save_and_git_worker():
    fake_decision = _fake_decision()
    pending = PendingProposal(knowledge=_fake_knowledge(), decision=fake_decision)

    with patch("app.api.proposals_routes.pop_proposal") as mock_pop, \
         patch("app.api.proposals_routes.run_save_worker") as mock_save_worker, \
         patch("app.api.proposals_routes.run_git_worker") as mock_git_worker:
        mock_pop.return_value = pending

        response = client.post("/api/proposals/abc-123/approve")

    assert response.status_code == 200
    assert response.json() == {"status": "saved", "target_path": fake_decision.target_path}
    mock_pop.assert_called_once_with("abc-123")
    mock_save_worker.assert_called_once_with(fake_decision)
    mock_git_worker.assert_called_once_with(fake_decision)


def test_approve_unknown_proposal_returns_404():
    with patch("app.api.proposals_routes.pop_proposal") as mock_pop:
        mock_pop.return_value = None

        response = client.post("/api/proposals/no-existe/approve")

    assert response.status_code == 404


def test_reject_proposal_returns_discarded():
    pending = PendingProposal(knowledge=_fake_knowledge(), decision=_fake_decision())

    with patch("app.api.proposals_routes.pop_proposal") as mock_pop:
        mock_pop.return_value = pending

        response = client.post("/api/proposals/abc-123/reject")

    assert response.status_code == 200
    assert response.json() == {"status": "discarded"}


def test_reject_unknown_proposal_returns_404():
    with patch("app.api.proposals_routes.pop_proposal") as mock_pop:
        mock_pop.return_value = None

        response = client.post("/api/proposals/no-existe/reject")

    assert response.status_code == 404
