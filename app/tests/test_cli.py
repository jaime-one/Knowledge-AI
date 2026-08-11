from unittest.mock import patch

from app.cli import review_decision
from app.models.decision_worker import DecisionOutput
from app.config.settings import settings


def test_review_decision_new_note_shows_content_and_approves(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(settings, "vault_path", str(tmp_path))
    decision = DecisionOutput(action="nueva", target_path="electricidad/nota.md", content="contenido nuevo")

    with patch("builtins.input", return_value="s"):
        approved = review_decision(decision)

    captured = capsys.readouterr()
    assert approved is True
    assert "contenido nuevo" in captured.out


def test_review_decision_edit_shows_diff_and_rejects(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(settings, "vault_path", str(tmp_path))
    note_dir = tmp_path / "electricidad"
    note_dir.mkdir()
    (note_dir / "nota.md").write_text("contenido viejo\n")

    decision = DecisionOutput(
        action="agregar",
        target_path="electricidad/nota.md",
        old_path="electricidad/nota.md",
        content="contenido viejo\ncontenido agregado\n",
    )

    with patch("builtins.input", return_value="n"):
        approved = review_decision(decision)

    captured = capsys.readouterr()
    assert approved is False
    assert "contenido agregado" in captured.out


def test_review_decision_rename_shows_rename_line_and_diffs_against_old_path(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(settings, "vault_path", str(tmp_path))
    note_dir = tmp_path / "nieve"
    note_dir.mkdir()
    (note_dir / "zapatos-nieve.md").write_text("contenido viejo\n")

    decision = DecisionOutput(
        action="agregar",
        target_path="nieve/articulos-nieve.md",
        old_path="nieve/zapatos-nieve.md",
        content="contenido viejo\ncontenido agregado\n",
    )

    with patch("builtins.input", return_value="n"):
        approved = review_decision(decision)

    captured = capsys.readouterr()
    assert approved is False
    assert "Renombrar: nieve/zapatos-nieve.md → nieve/articulos-nieve.md" in captured.out
    assert "contenido agregado" in captured.out
