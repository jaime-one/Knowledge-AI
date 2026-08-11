import uuid

from pydantic import BaseModel

from app.models.knowledge_worker import KnowledgeOutput
from app.models.decision_worker import DecisionOutput


class PendingProposal(BaseModel):
    knowledge: KnowledgeOutput
    decision: DecisionOutput


# Diccionario en memoria de proceso: requiere correr uvicorn con un solo worker
# (nunca --workers > 1, cada proceso tendría su propio diccionario vacío) y
# acepta que un restart del servidor pierde las propuestas pendientes.
_pending: dict[str, PendingProposal] = {}


def save_proposal(knowledge: KnowledgeOutput, decision: DecisionOutput) -> str:
    proposal_id = str(uuid.uuid4())
    _pending[proposal_id] = PendingProposal(knowledge=knowledge, decision=decision)
    return proposal_id


def pop_proposal(proposal_id: str) -> PendingProposal | None:
    return _pending.pop(proposal_id, None)
