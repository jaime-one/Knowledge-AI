from pydantic import BaseModel, Field

class ClassificationOutput(BaseModel):
    folder_path: str = Field(description="Ruta de carpeta/subcarpeta destino para la nota, ej. 'astronomia/galaxias'. Si ninguna carpeta existente encaja, proponer una nueva basada en el tema principal del contenido.")
    is_new_folder: bool = Field(description="True si folder_path no está entre las carpetas existentes provistas y hay que crearla.")
