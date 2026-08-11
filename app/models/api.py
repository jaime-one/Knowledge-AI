from pydantic import BaseModel, Field

from app.models.knowledge_worker import ConceptCorrection
from app.models.decision_worker import DecisionOutput


class VaultNoteInfo(BaseModel):
    path: str = Field(description="Ruta relativa de la nota dentro del vault, incluida la carpeta.")
    folder: str = Field(description="Carpeta contenedora de la nota, string vacío si está en la raíz del vault.")


class VaultNoteDetail(VaultNoteInfo):
    content: str = Field(description="Contenido crudo del archivo markdown, incluye frontmatter si existe.")


class DraftRequest(BaseModel):
    text: str = Field(min_length=1, description="Texto crudo de la nota a ingerir.")
    main_theme: str | None = Field(default=None, description="Tema principal sugerido por el usuario, opcional.")
    context: str | None = Field(default=None, description="Contexto adicional del usuario, opcional.")


class ProposalResponse(BaseModel):
    proposal_id: str = Field(description="Id de la propuesta pendiente, a usar en approve/reject.")
    decision: DecisionOutput
    corrections: list[ConceptCorrection] = Field(default_factory=list)


class ApprovalResponse(BaseModel):
    status: str
    target_path: str
