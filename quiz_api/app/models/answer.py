from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..database import Base


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    quiz_session_id = Column(Integer, ForeignKey("quiz_sessions.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    respuesta_seleccionada = Column(Integer, nullable=False)  # 0-based index
    es_correcta = Column(Boolean, default=False)
    tiempo_respuesta_segundos = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    quiz_session = relationship("QuizSession", back_populates="answers")
    question = relationship("Question", back_populates="answers")
