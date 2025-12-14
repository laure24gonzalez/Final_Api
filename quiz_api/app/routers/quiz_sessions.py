from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..database import get_db
from ..models.quiz_session import QuizSession
from ..models.answer import Answer
from ..schemas.quiz_session import QuizSessionCreate, QuizSessionRead, QuizSessionUpdate

router = APIRouter()


@router.post("/", response_model=QuizSessionRead)
def create_session(payload: QuizSessionCreate, db: Session = Depends(get_db)):
    """
    Iniciar una nueva sesión de quiz.
    
    Crea una nueva sesión con estado 'en_progreso' y registra la fecha/hora de inicio.
    El usuario puede proporcionar su nombre para identificación.
    
    Args:
        payload: Datos para crear la sesión (usuario_nombre es opcional)
        db: Sesión de base de datos
        
    Returns:
        QuizSessionRead: Sesión creada con su ID y datos iniciales
    """
    session = QuizSession(
        usuario_nombre=payload.usuario_nombre,
        estado="en_progreso"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/", response_model=List[QuizSessionRead])
def list_sessions(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Listar todas las sesiones de quiz con paginación.
    
    Retorna un listado de todas las sesiones (en cualquier estado).
    
    Args:
        db: Sesión de base de datos
        skip: Número de registros a saltar (default: 0)
        limit: Número máximo de registros a retornar (1-100, default: 10)
        
    Returns:
        List[QuizSessionRead]: Lista de sesiones
    """
    return db.query(QuizSession).offset(skip).limit(limit).all()


@router.get("/{session_id}", response_model=QuizSessionRead)
def get_session(session_id: int, db: Session = Depends(get_db)):
    """
    Obtener detalles completos de una sesión específica.
    
    Args:
        session_id: ID de la sesión a obtener
        db: Sesión de base de datos
        
    Returns:
        QuizSessionRead: Datos completos de la sesión
        
    Raises:
        HTTPException: Si la sesión no existe (404)
    """
    session = db.query(QuizSession).filter(QuizSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    return session


@router.put("/{session_id}/complete", response_model=QuizSessionRead)
def complete_session(session_id: int, db: Session = Depends(get_db)):
    """
    Finalizar una sesión de quiz y calcular la puntuación final.
    
    Cambia el estado a 'completado', registra la fecha de finalización,
    y calcula automáticamente:
    - Puntuación total (porcentaje de aciertos)
    - Número de preguntas respondidas y correctas
    - Tiempo total invertido
    
    Args:
        session_id: ID de la sesión a finalizar
        db: Sesión de base de datos
        
    Returns:
        QuizSessionRead: Sesión actualizada con la puntuación final
        
    Raises:
        HTTPException: Si la sesión no existe (404)
    """
    session = db.query(QuizSession).filter(QuizSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    # Obtener todas las respuestas de esta sesión
    answers = db.query(Answer).filter(Answer.quiz_session_id == session_id).all()
    
    # Calcular estadísticas
    preguntas_respondidas = len(answers)
    preguntas_correctas = sum(1 for a in answers if a.es_correcta)
    tiempo_total = sum(a.tiempo_respuesta_segundos for a in answers if a.tiempo_respuesta_segundos)
    
    # Calcular puntuación (100 * aciertos / respondidas)
    puntuacion = (preguntas_correctas * 100 // preguntas_respondidas) if preguntas_respondidas > 0 else 0
    
    session.fecha_fin = datetime.utcnow()
    session.preguntas_respondidas = preguntas_respondidas
    session.preguntas_correctas = preguntas_correctas
    session.puntuacion_total = puntuacion
    session.tiempo_total_segundos = tiempo_total if tiempo_total > 0 else None
    session.estado = "completado"
    
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.delete("/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    """
    Eliminar una sesión de quiz.
    
    Nota: Esta acción es irreversible y eliminará también todas 
    las respuestas asociadas a la sesión (por cascada).
    
    Args:
        session_id: ID de la sesión a eliminar
        db: Sesión de base de datos
        
    Returns:
        dict: Mensaje de confirmación
        
    Raises:
        HTTPException: Si la sesión no existe (404)
    """
    session = db.query(QuizSession).filter(QuizSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    db.delete(session)
    db.commit()
    return {"detail": "Sesión eliminada"}
