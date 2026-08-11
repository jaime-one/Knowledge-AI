from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate

from app.services.llm_factory import get_llm
from app.models.knowledge_worker import KnowledgeOutput

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "knowledge_worker.md"


def _build_guidance_block(main_theme: str | None, context: str | None) -> str:
    lines = []
    if main_theme:
        lines.append(f"Tema principal sugerido por el usuario: {main_theme}")
    if context:
        lines.append(f"Contexto adicional del usuario: {context}")
    if not lines:
        return ""
    return (
        "\n\n---\nGuía del usuario (orientación de enfoque, NO la trates "
        "como contenido a agregar):\n" + "\n".join(lines)
    )


def run_knowledge_worker(
    text: str,
    main_theme: str | None = None,
    context: str | None = None,
) -> KnowledgeOutput:
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input_text}{guidance_block}"),
    ])

    llm = get_llm("knowledge_worker")
    structured_llm = llm.with_structured_output(KnowledgeOutput)

    # completa: encadena prompt y structured_llm con el operador |
    chain = prompt | structured_llm

    return chain.invoke({
        "input_text": text,
        "guidance_block": _build_guidance_block(main_theme, context),
    })