from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api.main import app
from app.models.api import VaultNoteDetail, VaultNoteInfo

client = TestClient(app)


def test_get_notes_returns_vault_listing():
    fake_notes = [
        VaultNoteInfo(path="electricidad/tipos-de-corriente.md", folder="electricidad"),
        VaultNoteInfo(path="README.md", folder=""),
    ]

    with patch("app.api.vault_routes.list_notes") as mock_list_notes:
        mock_list_notes.return_value = fake_notes

        response = client.get("/api/notes")

    assert response.status_code == 200
    assert response.json() == [
        {"path": "electricidad/tipos-de-corriente.md", "folder": "electricidad"},
        {"path": "README.md", "folder": ""},
    ]


def test_get_notes_returns_empty_list_for_empty_vault():
    with patch("app.api.vault_routes.list_notes") as mock_list_notes:
        mock_list_notes.return_value = []

        response = client.get("/api/notes")

    assert response.status_code == 200
    assert response.json() == []


def test_get_note_returns_content_when_found():
    fake_note = VaultNoteDetail(
        path="electricidad/tipos-de-corriente.md",
        folder="electricidad",
        content="# Contenido real",
    )

    with patch("app.api.vault_routes.read_note") as mock_read_note:
        mock_read_note.return_value = fake_note

        response = client.get("/api/notes/electricidad/tipos-de-corriente.md")

    assert response.status_code == 200
    assert response.json() == {
        "path": "electricidad/tipos-de-corriente.md",
        "folder": "electricidad",
        "content": "# Contenido real",
    }


def test_get_note_returns_404_when_not_found():
    with patch("app.api.vault_routes.read_note") as mock_read_note:
        mock_read_note.return_value = None

        response = client.get("/api/notes/no-existe.md")

    assert response.status_code == 404


def test_get_note_returns_400_when_path_escapes_vault():
    with patch("app.api.vault_routes.read_note") as mock_read_note:
        mock_read_note.side_effect = ValueError("La ruta solicitada está fuera del vault.")

        response = client.get("/api/notes/..%2Ffuera-del-vault.md")

    assert response.status_code == 400
