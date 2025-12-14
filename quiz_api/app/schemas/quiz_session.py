from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class QuizSessionCreate(BaseModel):
    """Schema para iniciar una nueva sesión de quiz"""
    usuario_nombre: Optional[str] = None


class QuizSessionUpdate(BaseModel):
    """Schema para actualizar una sesión (completar)"""
    tiempo_total_segundos: Optional[int] = None


class QuizSessionRead(BaseModel):
    """Schema para leer una sesión de quiz"""
    id: int
    usuario_nombre: Optional[str]
    fecha_inicio: datetime
    fecha_fin: Optional[datetime]
    puntuacion_total: int
    preguntas_respondidas: int
    preguntas_correctas: int
    estado: str
    tiempo_total_segundos: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True
