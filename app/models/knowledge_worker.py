from pydantic import BaseModel, Field

class ConceptCorrection(BaseModel):
    concept: str = Field(description="El concepto o término en cuestión")
    user_understanding: str = Field(description="Cómo el usuario entendió/describió el concepto en su texto original")
    correct_explanation: str = Field(description="Explicación correcta del concepto, breve y clara")

class KnowledgeOutput(BaseModel):
    title: str = Field(description="Título propuesto para la nota, conciso y descriptivo")
    summary: str = Field(description="Resumen breve del contenido, 1-3 frases")
    key_concepts: list[str] = Field(description="Conceptos o entidades clave mencionados en el texto")
    content: str = Field(description="El conocimiento del usuario organizado y con gramática corregida, en Markdown con sub-headers (##, ###) si hay sub-temas naturales. No agregar información que no esté en el texto original.")
    corrections: list[ConceptCorrection] = Field(default_factory=list, description="Conceptos que el usuario parece haber entendido mal, con la aclaración correcta. Lista vacía si no se detectó ningún error conceptual.")