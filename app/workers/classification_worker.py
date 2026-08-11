from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate

from app.services.llm_factory import get_llm
from app.models.knowledge_worker import KnowledgeOutput
from app.models.classification_worker import ClassificationOutput

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "classification_worker.md"


def run_classification_worker(knowledge: KnowledgeOutput, existing_folders: list[str]) -> ClassificationOutput:
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Título: {title}\nResumen: {summary}\nConceptos clave: {key_concepts}\n\nCarpetas existentes:\n{existing_folders}"),
    ])

    llm = get_llm("classification_worker")
    structured_llm = llm.with_structured_output(ClassificationOutput)

    chain = prompt | structured_llm

    return chain.invoke({
        "title": knowledge.title,
        "summary": knowledge.summary,
        "key_concepts": ", ".join(knowledge.key_concepts),
        "existing_folders": "\n".join(f"- {folder}" for folder in existing_folders) if existing_folders else "(ninguna todavía, es la primera nota)",
    })
