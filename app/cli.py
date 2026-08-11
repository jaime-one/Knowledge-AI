import difflib
from pathlib import Path

from app.config.settings import settings
from app.models.decision_worker import DecisionOutput
from app.graph.ingestion_graph import run_ingestion_graph
from app.workers.save_worker import run_save_worker
from app.workers.git_worker import run_git_worker

#funcion con _ indica que es para este modulo no se importa i corre de otros lados
# solo aclara.
def _print_proposal(decision: DecisionOutput) -> None:
    print(f"Acción: {decision.action}")

    if decision.action == "nueva":
        print(f"Ruta destino: {decision.target_path}")
        print()
        print("Contenido nuevo:")
        print(decision.content)
        return

    if decision.old_path != decision.target_path:
        print(f"Renombrar: {decision.old_path} → {decision.target_path}")
    else:
        print(f"Ruta destino: {decision.target_path}")
    print()

    old_note_path = Path(settings.vault_path) / decision.old_path
    old_content = old_note_path.read_text(encoding="utf-8")
    diff = difflib.unified_diff(
        old_content.splitlines(keepends=True),
        decision.content.splitlines(keepends=True),
        fromfile="actual",
        tofile="propuesto",
    )
    print("Diff propuesto:")
    print("".join(diff))


def review_decision(decision: DecisionOutput) -> bool:
    _print_proposal(decision)
    respuesta = input("\n¿Apruebas este cambio? [s/N]: ").strip().lower()
    return respuesta == "s"


def run_cli(raw_text: str) -> tuple[DecisionOutput, bool]:
    knowledge, decision = run_ingestion_graph(raw_text)
    approved = review_decision(decision)
    return decision, approved


if __name__ == "__main__":
    nota = input("Escribe la nota:\n")
    decision, approved = run_cli(nota)

    if approved:
        run_save_worker(decision)
        run_git_worker(decision)
        print(f"Guardado y commiteado: {decision.target_path}")
    else:
        print("Descartado.")
