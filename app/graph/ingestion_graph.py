from typing import TypedDict
from langgraph.graph import StateGraph, START, END

from app.config.settings import settings
from app.models.knowledge_worker import KnowledgeOutput
from app.models.decision_worker import DecisionOutput
from app.workers.knowledge_worker import run_knowledge_worker
from app.workers.decision_worker import run_decision_worker
from app.services.vault import list_existing_folders


class IngestionState(TypedDict):
    raw_text: str
    main_theme: str | None
    context: str | None
    knowledge: KnowledgeOutput
    decision: DecisionOutput


def knowledge_node(state: IngestionState) -> dict:
    result = run_knowledge_worker(
        state["raw_text"],
        main_theme=state["main_theme"],
        context=state["context"],
    )
    return {"knowledge": result}


def decision_node(state: IngestionState) -> dict:
    existing_folders = list_existing_folders(settings.vault_path)
    result = run_decision_worker(state["knowledge"], existing_folders)
    return {"decision": result}


graph = StateGraph(IngestionState)
graph.add_node("knowledge_node", knowledge_node)
graph.add_node("decision_node", decision_node)
graph.add_edge(START, "knowledge_node")
graph.add_edge("knowledge_node", "decision_node")
graph.add_edge("decision_node", END)

ingestion_graph = graph.compile()


def run_ingestion_graph(
    raw_text: str,
    main_theme: str | None = None,
    context: str | None = None,
) -> tuple[KnowledgeOutput, DecisionOutput]:
    result = ingestion_graph.invoke({
        "raw_text": raw_text,
        "main_theme": main_theme,
        "context": context,
    })
    return result["knowledge"], result["decision"]
