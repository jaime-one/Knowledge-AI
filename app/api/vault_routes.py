from fastapi import APIRouter, HTTPException

from app.config.settings import settings
from app.models.api import VaultNoteDetail, VaultNoteInfo
from app.services.vault import list_notes, read_note

router = APIRouter()


@router.get("/notes", response_model=list[VaultNoteInfo])
def get_notes() -> list[VaultNoteInfo]:
    return list_notes(settings.vault_path)


@router.get("/notes/{note_path:path}", response_model=VaultNoteDetail)
def get_note(note_path: str) -> VaultNoteDetail:
    try:
        note = read_note(settings.vault_path, note_path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if note is None:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    return note
