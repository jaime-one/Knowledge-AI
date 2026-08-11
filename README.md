# KnowledgeAI — Backend

Backend for a personal knowledge base: raw text notes go in, an LLM pipeline turns them into structured Markdown notes, decides whether they're new or should update an existing note, and keeps a vector index in sync for semantic search. A human approves every write before anything touches disk or git.

Markdown is the source of truth. The vector index (ChromaDB) is just a disposable, regenerable index on top of it.

## How it works

```
raw text
   │
   ▼
Knowledge Worker      → extracts title, summary, key concepts, cleaned content
   │
   ▼
Decision Worker (agent) → tool-calls Retrieval / Classification / Markdown / read_note
                           to decide: new note, edit, or merge into an existing one
   │
   ▼
human review (CLI or API)  → approve / reject
   │
   ▼
Save Worker  → writes the .md file, re-chunks + re-embeds it in Chroma
   │
   ▼
Git Worker   → commits and pushes the change to the vault repo
```

The Decision Worker is the only agentic step: it's an LLM bound to tools (vector search, folder classification, markdown formatting, reading an existing note) that loops on tool calls until it has enough context to output a structured decision.

## Project structure

```
app/
├── api/         FastAPI app + routes (proposal creation/approval, vault browsing)
├── cli.py       Terminal entrypoint: paste text, review a diff, approve/reject
├── config/      Settings (.env) and per-worker LLM config (models.yaml)
├── graph/       LangGraph graph wiring Knowledge Worker → Decision Worker
├── models/      Pydantic schemas for each worker's structured output
├── prompts/     System prompts for the LLM-backed workers
├── services/    LLM factory, Chroma client, vault filesystem helpers, proposal store
├── workers/     One module per pipeline step (below)
└── tests/       pytest suite, one file per worker/route
langgraph.json   Manifest to run the graph locally with LangGraph Studio
```

## Workers

| Worker | Responsibility |
|---|---|
| `knowledge_worker` | Structures raw text into title, summary, key concepts and cleaned content |
| `classification_worker` | Picks the target folder/subfolder for a genuinely new note |
| `decision_worker` | Orchestrating agent — decides new / edit / merge and produces the final content |
| `markdown_worker` | Renders content with YAML frontmatter and a filename slug |
| `chunk_worker` | Splits a note into header-based chunks |
| `embedding_worker` | Embeds chunks and upserts them into ChromaDB |
| `retrieval_worker` | Semantic search over the Chroma collection (used by the Decision Worker) |
| `save_worker` | Writes the approved note to disk, re-chunks/re-embeds it, cleans up stale entries on rename |
| `git_worker` | Commits and pushes the change to the vault repository |

## API

- `POST /api/proposals` — run the ingestion graph on raw text, return a pending proposal.
- `POST /api/proposals/{id}/approve` — persist an approved proposal (Save + Git worker).
- `POST /api/proposals/{id}/reject` — discard a pending proposal.
- `GET /api/notes` / `GET /api/notes/{path}` — browse the vault.

## Stack

- **FastAPI** + **Uvicorn** — HTTP API
- **LangGraph** + **LangChain** (`langchain-anthropic`, `langchain-openai`) — orchestration and structured LLM calls
- **ChromaDB** — local vector store
- **Pydantic** / **pydantic-settings** — schemas and config
- **uv** — dependency management
- **pytest** — tests
- **LangSmith** — optional tracing

## Running locally

```bash
uv sync
cp .env.example .env   # fill in the keys below
uvicorn app.api.main:app --reload
# or, for the terminal flow:
uv run python -m app.cli
```

Required environment variables (`.env`):

| Variable | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | Claude models |
| `GPT_API_KEY` | OpenAI models (classification, markdown, embeddings) |
| `VAULT_PATH` | Path to the Markdown vault (separate git repo) |
| `DEBUG` | Optional, defaults to `false` |
| `LANGSMITH_TRACING`, `LANGSMITH_ENDPOINT`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT` | Optional, LangSmith tracing |

## Tests

```bash
uv run pytest
```
