# KnowledgeAI — Guía para Claude Code en este repo

## Qué es este proyecto

KnowledgeAI es un Second Brain / PKM personal: convierte notas, documentos y (a futuro) audio en una base de conocimiento en Markdown, indexada con embeddings para RAG. Filosofía central (no negociable):

```
Markdown    = fuente de verdad
Embeddings  = índice (regenerable, descartable)
LLM         = editor, no la memoria
```

Visión completa y arquitectura de referencia: `../plan.md` (documento de visión original, fuera de este repo — no editar desde aquí).

## Cómo colaborar en este repo (regla de oro)

**El usuario escribe el código él mismo.** El propósito explícito de este proyecto es que aprenda AI Engineering (LangGraph, RAG, structured output, testing de sistemas con LLMs, observabilidad) construyéndolo, no que la app exista lo antes posible.

Cuando trabajes aquí:
- Explica el concepto antes de que se escriba código (el porqué, no solo el qué).
- Señala documentación real (LangGraph, LangChain, Pydantic, FastAPI) en vez de resumirla de memoria cuando haya duda.
- Revisa lo que el usuario escribe — no lo reescribas por él salvo que lo pida explícitamente.
- Da comandos exactos para que él los corra y reporte el resultado, en vez de ejecutarlos tú mismo, salvo tareas puramente mecánicas de verificación (lectura de archivos, `git status`, tests).

## Alcance actual: Etapa 1

- Solo ingesta de **texto** (notas/markdown pegado). Nada de audio ni imágenes ni PDFs todavía (Etapa 2).
- Orquestación con **LangGraph desde el inicio** (decisión explícita del usuario).
- El Decision Worker (crear/editar/fusionar) **solo propone** — nunca escribe sin aprobación humana explícita (diff + confirmación por CLI).
- Sin UI visual esta etapa: FastAPI (`/docs`) + CLI. La integración visual queda para una etapa futura.
- Entorno con `uv`.

## Topología de repos (importante, no es un solo repo)

```
KnowledgeAI/                 <- carpeta contenedora, NO es un repo git
├── Backend/
│   ├── plan.md              <- doc de visión, fuera de cualquier repo (intencional)
│   └── knowledge_ai/        <- ESTE repo (código) — repo git independiente
│       ├── claude.md        <- este archivo
│       ├── aprendizaje.md   <- bitácora de aprendizaje (ver abajo)
│       ├── app/
│       └── chroma/          <- índice vectorial local, gitignored, regenerable
├── FrontendWeb/              <- sin repo todavía, fuera de alcance de esta etapa
└── knowledge/                <- repo git INDEPENDIENTE (el vault, la fuente de verdad)
```

`knowledge/` y `Backend/knowledge_ai/` son carpetas hermanas (ninguna contiene a la otra), así que son dos repos completamente independientes sin problema de anidamiento. Cada uno tendrá su propio remoto en GitHub cuando el usuario decida — nunca hacer `git push` sin que lo pida explícitamente.

## Bitácora de aprendizaje

`aprendizaje.md` (en esta misma carpeta) es un resumen curado de conceptos y decisiones, **no un log automático** — se actualiza solo cuando el usuario lo pide explícitamente (ej. "guarda en aprendizaje.md los conceptos de UV y los pasos que usamos hoy"). Mantenlo limpio y en sus propias palabras cuando sea posible, no un volcado de la conversación.

## Progreso (Etapa 1 — actualizar al cerrar cada milestone)

- [ ] M0 — Entorno, estructura de carpetas y Git
- [ ] M1 — Configuración centralizada (.env + models.yaml)
- [ ] M2 — LLM Factory
- [ ] M3 — Knowledge Worker
- [ ] M4 — Markdown Worker
- [ ] M5 — Chunk + Embedding Worker + ChromaDB
- [ ] M6 — Retrieval Worker
- [ ] M7 — Classification Worker
- [ ] M8 — Decision Worker
- [ ] M9 — Ejercicio LangGraph Hello World
- [ ] M10 — Ensamblar grafo real de ingesta
- [ ] M11 — Human-in-the-loop + CLI
- [ ] M12 — Save Worker + Git Worker
- [ ] M13 — FastAPI + búsqueda CLI
- [ ] M14 — Observabilidad LangSmith
- [ ] M15 — Pulido, documentación y aceptación
