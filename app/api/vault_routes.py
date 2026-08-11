from fastapi import APIRouter

from app.config.settings import settings
from app.models.api import VaultNoteInfo
from app.services.vault import list_notes

router = APIRouter()


@router.get("/notes", response_model=list[VaultNoteInfo])
def get_notes() -> list[VaultNoteInfo]:
    return list_notes(settings.vault_path)
