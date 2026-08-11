from unittest.mock import MagicMock, patch
from langchain_core.runnables import Runnable

from app.models.knowledge_worker import KnowledgeOutput
from app.models.classification_worker import ClassificationOutput
from app.workers.classification_worker import run_classification_worker


def test_run_classification_worker_returns_llm_output():
    fake_knowledge = KnowledgeOutput(
        title="Tipos de corriente eléctrica",
        summary="Diferencias entre corriente continua y corriente alterna.",
        key_concepts=["corriente continua", "corriente alterna"],
        content="Contenido de prueba",
        corrections=[],
    )
    fake_output = ClassificationOutput(
        folder_path="electricidad",
        is_new_folder=True,
    )

    with patch("app.workers.classification_worker.get_llm") as mock_get_llm:
        mock_structured_llm = MagicMock(spec=Runnable)
        mock_structured_llm.invoke.return_value = fake_output
        #Flujo que ocurre realmente en la funcion run_classification_worker
        mock_get_llm.return_value.with_structured_output.return_value = mock_structured_llm

        result = run_classification_worker(fake_knowledge, existing_folders=["astronomia/galaxias"])

    assert result == fake_output
