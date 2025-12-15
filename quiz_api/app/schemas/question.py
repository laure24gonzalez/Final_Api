from pydantic import BaseModel, field_validator, ValidationInfo
from datetime import datetime
from ..services.quiz_service import canonical_category, canonical_difficulty


class QuestionCreate(BaseModel):
    """Schema para crear una nueva pregunta"""
    pregunta: str
    opciones: list[str]
    respuesta_correcta: int
    explicacion: str | None = None
    categoria: str
    dificultad: str

    @field_validator("opciones")
    @classmethod
    def validate_opciones(cls, v: list[str]) -> list[str]:
        """Validar que haya entre 3 y 5 opciones"""
        if not (3 <= len(v) <= 5):
            raise ValueError("Debe haber entre 3 y 5 opciones")
        return v

    @field_validator("respuesta_correcta")
    @classmethod
    def validate_respuesta_correcta(cls, v: int, info: ValidationInfo) -> int:
        """Validar que el índice de respuesta correcta sea válido"""
        opciones = info.data.get("opciones", [])
        if not (0 <= v < len(opciones)):
            raise ValueError(f"respuesta_correcta debe estar entre 0 y {len(opciones) - 1}")
        return v

    @field_validator("categoria")
    @classmethod
    def validate_categoria(cls, v: str) -> str:
        """Validar que la categoría sea válida"""
        try:
            return canonical_category(v)
        except ValueError as e:
            raise ValueError(str(e))

    @field_validator("dificultad")
    @classmethod
    def validate_dificultad(cls, v: str) -> str:
        """Validar que la dificultad sea válida"""
        try:
            return canonical_difficulty(v)
        except ValueError as e:
            raise ValueError(str(e))


class QuestionRead(BaseModel):
    """Schema para leer una pregunta"""
    id: int
    pregunta: str
    opciones: list[str]
    respuesta_correcta: int
    explicacion: str | None
    categoria: str
    dificultad: str
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True
