from pathlib import Path

from app.models.api import VaultNoteDetail, VaultNoteInfo


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


def read_note(vault_path: str, note_path: str) -> VaultNoteDetail | None:
    root = Path(vault_path).resolve()
    candidate = (root / note_path).resolve()

    if not candidate.is_relative_to(root):
        raise ValueError("La ruta solicitada está fuera del vault.")

    relative = candidate.relative_to(root)
    if any(part.startswith(".") for part in relative.parts):
        return None
    if not candidate.is_file() or candidate.suffix != ".md":
        return None

    content = candidate.read_text(encoding="utf-8")
    folder = str(relative.parent) if relative.parent != Path(".") else ""
    return VaultNoteDetail(path=str(relative), folder=folder, content=content)
