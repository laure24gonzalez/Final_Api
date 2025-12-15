from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AnswerCreate(BaseModel):
    """Schema para registrar una respuesta del usuario"""
    quiz_session_id: int
    question_id: int
    respuesta_seleccionada: int
    tiempo_respuesta_segundos: Optional[int] = None


class AnswerRead(BaseModel):
    """Schema para leer una respuesta registrada"""
    id: int
    quiz_session_id: int
    question_id: int
    respuesta_seleccionada: int
    es_correcta: bool
    tiempo_respuesta_segundos: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True
