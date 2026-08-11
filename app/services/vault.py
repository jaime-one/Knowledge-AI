from pathlib import Path

from app.models.api import VaultNoteInfo


def list_existing_folders(vault_path: str) -> list[str]:
    root = Path(vault_path)
    return [
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.is_dir() and not path.name.startswith(".")
    ]


def list_notes(vault_path: str) -> list[VaultNoteInfo]:
    root = Path(vault_path)
    notes = []
    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root)
        if any(part.startswith(".") for part in relative.parts):
            continue
        folder = str(relative.parent) if relative.parent != Path(".") else ""
        notes.append(VaultNoteInfo(path=str(relative), folder=folder))
    return notes
