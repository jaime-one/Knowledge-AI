from unittest.mock import patch

from app.models.decision_worker import DecisionOutput
from app.workers.git_worker import run_git_worker
from app.config.settings import settings


def test_run_git_worker_adds_and_commits(monkeypatch):
    monkeypatch.setattr(settings, "vault_path", "/fake/vault")
    decision = DecisionOutput(action="nueva", target_path="electricidad/nota.md", content="contenido")

    with patch("app.workers.git_worker.subprocess.run") as mock_run:
        run_git_worker(decision)

    assert mock_run.call_count == 3
    mock_run.assert_any_call(
        ["git", "add", "electricidad/nota.md"], cwd="/fake/vault", check=True
    )
    mock_run.assert_any_call(
        ["git", "commit", "-m", "nueva: electricidad/nota.md"],
        cwd="/fake/vault",
        check=True,
    )
    mock_run.assert_any_call(["git", "push"], cwd="/fake/vault", check=True)


def test_run_git_worker_rename_adds_both_paths_and_commits_rename_message(monkeypatch):
    monkeypatch.setattr(settings, "vault_path", "/fake/vault")
    decision = DecisionOutput(
        action="agregar",
        target_path="nieve/articulos-nieve.md",
        old_path="nieve/zapatos-nieve.md",
        content="contenido",
    )

    with patch("app.workers.git_worker.subprocess.run") as mock_run:
        run_git_worker(decision)

    assert mock_run.call_count == 4
    mock_run.assert_any_call(
        ["git", "add", "nieve/articulos-nieve.md"], cwd="/fake/vault", check=True
    )
    mock_run.assert_any_call(
        ["git", "add", "nieve/zapatos-nieve.md"], cwd="/fake/vault", check=True
    )
    mock_run.assert_any_call(
        ["git", "commit", "-m", "agregar: nieve/zapatos-nieve.md -> nieve/articulos-nieve.md"],
        cwd="/fake/vault",
        check=True,
    )
    mock_run.assert_any_call(["git", "push"], cwd="/fake/vault", check=True)
