from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..database import Base


class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    id = Column(Integer, primary_key=True, index=True)
    usuario_nombre = Column(String, nullable=True)
    fecha_inicio = Column(DateTime, default=datetime.now(timezone.utc))
    fecha_fin = Column(DateTime, nullable=True)
    puntuacion_total = Column(Integer, default=0)
    preguntas_respondidas = Column(Integer, default=0)
    preguntas_correctas = Column(Integer, default=0)
    estado = Column(String, default="en_progreso")  # "en_progreso", "completado", "abandonado"
    tiempo_total_segundos = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    answers = relationship("Answer", back_populates="quiz_session", cascade="all, delete-orphan")
