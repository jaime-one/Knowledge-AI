from typing import Literal
from pydantic import BaseModel, Field, field_validator, model_validator

class DecisionOutput(BaseModel):
    action: Literal["nueva", "editar", "agregar"] = Field(description="Qué decidió hacer con el contenido nuevo.")
    target_path: str = Field(description="Ruta final del archivo .md (carpeta/subcarpeta/filename), sea nota nueva o existente.")
    old_path: str | None = Field(
        default=None,
        description="Ruta de la nota existente antes de esta decisión (la que se leyó con read_note_tool). None si action es 'nueva'. Para 'editar'/'agregar' es igual a target_path salvo que se proponga renombrar el archivo.",
    )
    content: str = Field(description="Contenido markdown final a guardar — completo, ya sea nota nueva o resultado de la fusión.")

    @field_validator("old_path", mode="before")
    @classmethod
    def _blank_string_to_none(cls, value: str | None) -> str | None:
        # El LLM a veces interpreta "vacío" como string vacío ("") en vez de
        # null — se normaliza aquí para no depender de que la generación sea
        # perfecta (ver también la regla 6 del prompt, que ataca la causa).
        if isinstance(value, str) and value.strip() == "":
            return None
        return value

    @model_validator(mode="after")
    def _old_path_matches_action(self) -> "DecisionOutput":
        if self.action == "nueva" and self.old_path is not None:
            raise ValueError("old_path debe ser None cuando action es 'nueva'.")
        if self.action != "nueva" and self.old_path is None:
            raise ValueError("old_path es obligatorio cuando action es 'editar' o 'agregar'.")
        return self
