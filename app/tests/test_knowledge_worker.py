from unittest.mock import MagicMock, patch
from langchain_core.runnables import Runnable

from app.models.knowledge_worker import KnowledgeOutput
from app.workers.knowledge_worker import _build_guidance_block, run_knowledge_worker


def test_run_knowledge_worker_returns_llm_output():
    fake_output = KnowledgeOutput(
        title="Título de prueba",
        summary="Resumen de prueba",
        key_concepts=["A", "B"],
        content="Contenido de prueba",
        corrections=[],
    )

    with patch("app.workers.knowledge_worker.get_llm") as mock_get_llm:
        mock_structured_llm = MagicMock(spec=Runnable)
        mock_structured_llm.invoke.return_value = fake_output
        #Flujo que ocurre realmente en la funcion run_knowledge_worker
        mock_get_llm.return_value.with_structured_output.return_value = mock_structured_llm

        result = run_knowledge_worker("cualquier texto de entrada")

    assert result == fake_output


def test_run_knowledge_worker_passes_empty_guidance_block_by_default():
    fake_output = KnowledgeOutput(
        title="Título de prueba",
        summary="Resumen de prueba",
        key_concepts=["A", "B"],
        content="Contenido de prueba",
        corrections=[],
    )

    with patch("app.workers.knowledge_worker.get_llm") as mock_get_llm:
        mock_structured_llm = MagicMock(spec=Runnable)
        mock_structured_llm.invoke.return_value = fake_output
        mock_get_llm.return_value.with_structured_output.return_value = mock_structured_llm

        run_knowledge_worker("cualquier texto de entrada")

        # prompt es un ChatPromptTemplate real (no mockeado), así que structured_llm.invoke
        # recibe el ChatPromptValue ya renderizado, no el diccionario crudo.
        prompt_value = mock_structured_llm.invoke.call_args.args[0]
        human_message = prompt_value.to_messages()[-1].content

    assert human_message == "cualquier texto de entrada"


def test_run_knowledge_worker_passes_guidance_block_when_provided():
    fake_output = KnowledgeOutput(
        title="Título de prueba",
        summary="Resumen de prueba",
        key_concepts=["A", "B"],
        content="Contenido de prueba",
        corrections=[],
    )

    with patch("app.workers.knowledge_worker.get_llm") as mock_get_llm:
        mock_structured_llm = MagicMock(spec=Runnable)
        mock_structured_llm.invoke.return_value = fake_output
        mock_get_llm.return_value.with_structured_output.return_value = mock_structured_llm

        run_knowledge_worker(
            "cualquier texto de entrada",
            main_theme="avalanchas",
            context="curso de montañismo",
        )

        prompt_value = mock_structured_llm.invoke.call_args.args[0]
        human_message = prompt_value.to_messages()[-1].content

    assert human_message.startswith("cualquier texto de entrada")
    assert "avalanchas" in human_message
    assert "curso de montañismo" in human_message


def test_build_guidance_block_with_theme_and_context():
    block = _build_guidance_block("avalanchas", "curso de montañismo")

    assert "Tema principal sugerido por el usuario: avalanchas" in block
    assert "Contexto adicional del usuario: curso de montañismo" in block


def test_build_guidance_block_with_only_theme():
    block = _build_guidance_block("avalanchas", None)

    assert "Tema principal sugerido por el usuario: avalanchas" in block
    assert "Contexto adicional" not in block


def test_build_guidance_block_with_only_context():
    block = _build_guidance_block(None, "curso de montañismo")

    assert "Contexto adicional del usuario: curso de montañismo" in block
    assert "Tema principal" not in block


def test_build_guidance_block_with_neither_returns_empty_string():
    assert _build_guidance_block(None, None) == ""
    assert _build_guidance_block("", "") == ""