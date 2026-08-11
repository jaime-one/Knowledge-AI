from fastapi import APIRouter, HTTPException

from app.models.api import ApprovalResponse, DraftRequest, ProposalResponse
from app.graph.ingestion_graph import run_ingestion_graph
from app.services.proposal_store import save_proposal, pop_proposal
from app.workers.save_worker import run_save_worker
from app.workers.git_worker import run_git_worker

router = APIRouter()


@router.post("/proposals", response_model=ProposalResponse)
def create_proposal(body: DraftRequest) -> ProposalResponse:
    try:
        knowledge, decision = run_ingestion_graph(
            body.text, main_theme=body.main_theme, context=body.context
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    proposal_id = save_proposal(knowledge, decision)
    return ProposalResponse(
        proposal_id=proposal_id,
        decision=decision,
        corrections=knowledge.corrections,
    )


@router.post("/proposals/{proposal_id}/approve", response_model=ApprovalResponse)
def approve_proposal(proposal_id: str) -> ApprovalResponse:
    proposal = pop_proposal(proposal_id)
    if proposal is None:
        raise HTTPException(status_code=404, detail="Propuesta no encontrada o ya resuelta")

    try:
        run_save_worker(proposal.decision)
        run_git_worker(proposal.decision)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return ApprovalResponse(status="saved", target_path=proposal.decision.target_path)


@router.post("/proposals/{proposal_id}/reject")
def reject_proposal(proposal_id: str) -> dict[str, str]:
    proposal = pop_proposal(proposal_id)
    if proposal is None:
        raise HTTPException(status_code=404, detail="Propuesta no encontrada o ya resuelta")
    return {"status": "discarded"}
