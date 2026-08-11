from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool

from app.services.llm_factory import get_llm
from app.config.settings import settings
from app.models.knowledge_worker import KnowledgeOutput
from app.models.decision_worker import DecisionOutput
from app.workers.retrieval_worker import run_retrieval_worker
from app.workers.classification_worker import run_classification_worker
from app.workers.markdown_worker import run_markdown_worker, slugify

import json

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "decision_worker.md"
DEBUG_DIR = Path(__file__).parent.parent.parent / "debug"


def run_decision_worker(knowledge: KnowledgeOutput, existing_folders: list[str]) -> DecisionOutput:
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    @tool
    def retrieval_tool(query: str) -> list[dict]:
        """Busca en la base vectorial (Chroma) chunks de notas existentes relacionados
        con `query`. Devuelve una lista de matches con 'content', 'metadata'
        (incluye 'source', la ruta de la nota dentro del vault) y 'distance'
        (menor = más similar)."""
        matches = run_retrieval_worker(query)
        return [match.model_dump() for match in matches]

    @tool
    def classification_tool() -> dict:
        """Decide la carpeta/subcarpeta destino para esta nota. Usar solo si se
        determinó que el contenido es información nueva, sin relación con
        ninguna nota existente."""
        result = run_classification_worker(knowledge, existing_folders)
        return result.model_dump()

    @tool
    def markdown_tool() -> dict:
        """Formatea el contenido de la nota nueva en markdown con frontmatter.
        Usar solo para notas nuevas."""
        result = run_markdown_worker(knowledge)
        return result.model_dump()

    @tool
    def read_note_tool(source_path: str) -> str:
        """Lee el contenido completo de una nota existente del vault, dado su
        'source' (tal como aparece en la metadata devuelta por retrieval_tool).
        Usar cuando una nota existente parece relacionada y hay que decidir si
        editarla o agregarle contenido."""
        note_path = Path(settings.vault_path) / source_path
        return note_path.read_text(encoding="utf-8")

    @tool
    def slugify_tool(title: str) -> str:
        """Convierte un título en un nombre de archivo .md válido (minúsculas,
        sin tildes, separado por guiones) — la misma convención que usan las
        notas nuevas. Usar únicamente si decidís renombrar una nota existente
        porque su alcance creció más allá del título/nombre actual, para que
        el nuevo nombre siga esa convención en vez de escribirlo a mano."""
        return f"{slugify(title)}.md"

    tools = [retrieval_tool, classification_tool, markdown_tool, read_note_tool, slugify_tool]
    #tools tiene atributo name. nombre de cada tool
    tools_by_name = {t.name: t for t in tools}

    llm = get_llm("decision_worker")
    llm_with_tools = llm.bind_tools(tools)

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Título: {title}\nResumen: {summary}\nConceptos clave: {key_concepts}\nContenido:\n{content}"),
    ])

    messages = prompt.format_messages(
        title=knowledge.title,
        summary=knowledge.summary,
        key_concepts=", ".join(knowledge.key_concepts),
        content=knowledge.content,
    )


    #Para entender los mensajes antes y despues:
    DEBUG_DIR.mkdir(exist_ok=True)

    def _dump_messages(filename: str):
        (DEBUG_DIR / filename).write_text(
            json.dumps([m.model_dump() for m in messages], indent=2)
        )

    _dump_messages("messages_before.json")

    # Bucle de tool-calling: el modelo pide herramientas hasta tener todo lo
    # que necesita para decidir. Sin LangGraph todavía (eso es M9/M10), así
    # que el bucle se controla a mano.
    step = 0
    while True:
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            break

        for tool_call in response.tool_calls:
            tool_fn = tools_by_name[tool_call["name"]]
            tool_result = tool_fn.invoke(tool_call["args"])
            messages.append(ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"]))

        _dump_messages(f"messages_step_{step}.json")
        step += 1

    _dump_messages("messages_after.json")

    # Llamada final: con todo el contexto ya reunido, se pide la decisión estructurada.
    structured_llm = llm.with_structured_output(DecisionOutput)
    return structured_llm.invoke(messages)
