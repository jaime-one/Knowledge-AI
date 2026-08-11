import subprocess

from app.config.settings import settings
from app.models.decision_worker import DecisionOutput


def run_git_worker(decision: DecisionOutput) -> None:
    is_rename = decision.old_path is not None and decision.old_path != decision.target_path

    subprocess.run(["git", "add", decision.target_path], cwd=settings.vault_path, check=True)
    if is_rename:
        subprocess.run(["git", "add", decision.old_path], cwd=settings.vault_path, check=True)

    message = f"{decision.action}: {decision.target_path}"
    if is_rename:
        message = f"{decision.action}: {decision.old_path} -> {decision.target_path}"

    subprocess.run(
        ["git", "commit", "-m", message],
        cwd=settings.vault_path,
        check=True,
    )
    subprocess.run(["git", "push"], cwd=settings.vault_path, check=True)
