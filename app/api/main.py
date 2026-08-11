from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.vault_routes import router as vault_router
from app.api.proposals_routes import router as proposals_router

app = FastAPI(title="KnowledgeAI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vault_router, prefix="/api")
app.include_router(proposals_router, prefix="/api")


@app.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}
