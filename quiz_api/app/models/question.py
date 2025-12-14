from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    pregunta = Column(String, nullable=False)
    opciones = Column(JSON, nullable=False)  # Array de strings: ["opción1", "opción2", ...]
    respuesta_correcta = Column(Integer, nullable=False)  # 0-based index
    explicacion = Column(Text, nullable=True)
    categoria = Column(String, nullable=False)  # "Tecnología", "Historia", "Ciencia", etc.
    dificultad = Column(String, nullable=False)  # "fácil", "medio", "difícil"
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")
