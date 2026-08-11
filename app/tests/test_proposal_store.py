from app.models.knowledge_worker import KnowledgeOutput
from app.models.decision_worker import DecisionOutput
from app.services.proposal_store import save_proposal, pop_proposal


def _fake_knowledge() -> KnowledgeOutput:
    return KnowledgeOutput(
        title="Tipos de corriente eléctrica",
        summary="Diferencias entre corriente continua y corriente alterna.",
        key_concepts=["corriente continua", "corriente alterna"],
        content="Contenido de prueba",
        corrections=[],
    )


def _fake_decision() -> DecisionOutput:
    return DecisionOutput(
        action="nueva",
        target_path="electricidad/tipos-de-corriente-electrica.md",
        content="contenido final",
    )


def test_save_then_pop_returns_same_proposal():
    knowledge = _fake_knowledge()
    decision = _fake_decision()

    proposal_id = save_proposal(knowledge, decision)
    proposal = pop_proposal(proposal_id)

    assert proposal is not None
    assert proposal.knowledge == knowledge
    assert proposal.decision == decision


def test_pop_removes_proposal_from_store():
    proposal_id = save_proposal(_fake_knowledge(), _fake_decision())

    pop_proposal(proposal_id)
    second_pop = pop_proposal(proposal_id)

    assert second_pop is None


def test_pop_unknown_id_returns_none():
    assert pop_proposal("no-existe") is None


def test_save_proposal_generates_distinct_ids():
    first_id = save_proposal(_fake_knowledge(), _fake_decision())
    second_id = save_proposal(_fake_knowledge(), _fake_decision())

    assert first_id != second_id
