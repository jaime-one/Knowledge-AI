from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api.main import app
from app.models.api import VaultNoteInfo

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
