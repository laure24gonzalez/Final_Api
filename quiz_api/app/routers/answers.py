from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import cast
from ..database import get_db
from ..models.answer import Answer
from ..models.question import Question
from ..models.quiz_session import QuizSession
from ..schemas.answer import AnswerCreate, AnswerRead

router = APIRouter()


@router.post("/", response_model=AnswerRead)
def register_answer(payload: AnswerCreate, db: Session = Depends(get_db)):
    """
    Registrar una respuesta del usuario.
    
    Valida que:
    - La sesión y pregunta existan
    - El índice de respuesta sea válido (0 al número de opciones - 1)
    - No exista respuesta duplicada para la misma pregunta en la sesión
    
    Calcula automáticamente si la respuesta es correcta.
    
    Args:
        payload: Datos de la respuesta (quiz_session_id, question_id, 
                 respuesta_seleccionada, tiempo_respuesta_segundos)
        db: Sesión de base de datos
        
    Returns:
        AnswerRead: Respuesta creada con su ID y corrección automática
        
    Raises:
        HTTPException: Si sesión/pregunta no existe (404) o datos inválidos (400)
    """
    # Validar que la sesión existe
    session = db.query(QuizSession).filter(QuizSession.id == payload.quiz_session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    # Validar que la pregunta existe
    question = db.query(Question).filter(Question.id == payload.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    
    # Validar que respuesta_seleccionada está en rango válido
    opciones_list = cast(list[str], question.opciones) if isinstance(question.opciones, list) else []
    if not (0 <= payload.respuesta_seleccionada < len(opciones_list)):
        raise HTTPException(
            status_code=400,
            detail=f"respuesta_seleccionada debe estar entre 0 y {len(opciones_list) - 1}"
        )
    
    # Validar que no hay respuesta duplicada para la misma pregunta en una sesión
    existing = db.query(Answer).filter(
        Answer.quiz_session_id == payload.quiz_session_id,
        Answer.question_id == payload.question_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Ya existe una respuesta para esta pregunta en esta sesión"
        )
    
    # Determinar si la respuesta es correcta
    es_correcta = (payload.respuesta_seleccionada == question.respuesta_correcta)
    
    # Crear respuesta
    answer = Answer(
        quiz_session_id=payload.quiz_session_id,
        question_id=payload.question_id,
        respuesta_seleccionada=payload.respuesta_seleccionada,
        es_correcta=es_correcta,
        tiempo_respuesta_segundos=payload.tiempo_respuesta_segundos
    )
    
    db.add(answer)
    db.commit()
    db.refresh(answer)
    return answer


@router.get("/session/{session_id}", response_model=list[AnswerRead])
def get_answers_by_session(
    session_id: int,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """
    Obtener todas las respuestas de una sesión específica.
    
    Retorna un listado de todas las respuestas registradas en una sesión,
    incluyendo si fueron correctas o no.
    
    Args:
        session_id: ID de la sesión
        db: Sesión de base de datos
        skip: Número de registros a saltar (default: 0)
        limit: Número máximo de registros a retornar (1-100, default: 100)
        
    Returns:
        List[AnswerRead]: Lista de respuestas de la sesión
        
    Raises:
        HTTPException: Si la sesión no existe (404)
    """
    # Validar que la sesión existe
    session = db.query(QuizSession).filter(QuizSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    return db.query(Answer).filter(
        Answer.quiz_session_id == session_id
    ).offset(skip).limit(limit).all()


@router.get("/{answer_id}", response_model=AnswerRead)
def get_answer(answer_id: int, db: Session = Depends(get_db)):
    """
    Obtener detalles completos de una respuesta específica.
    
    Args:
        answer_id: ID de la respuesta a obtener
        db: Sesión de base de datos
        
    Returns:
        AnswerRead: Datos completos de la respuesta
        
    Raises:
        HTTPException: Si la respuesta no existe (404)
    """
    answer = db.query(Answer).filter(Answer.id == answer_id).first()
    if not answer:
        raise HTTPException(status_code=404, detail="Respuesta no encontrada")
    return answer


@router.put("/{answer_id}", response_model=AnswerRead)
def update_answer(answer_id: int, payload: AnswerCreate, db: Session = Depends(get_db)):
    """
    Actualizar una respuesta registrada (para correcciones).
    
    Permite cambiar la respuesta seleccionada y recalcula automáticamente
    si es correcta. También puede actualizar el tiempo de respuesta.
    
    Args:
        answer_id: ID de la respuesta a actualizar
        payload: Nuevos datos de la respuesta
        db: Sesión de base de datos
        
    Returns:
        AnswerRead: Respuesta actualizada
        
    Raises:
        HTTPException: Si la respuesta/pregunta no existe (404) o datos inválidos (400)
    """
    answer = db.query(Answer).filter(Answer.id == answer_id).first()
    if not answer:
        raise HTTPException(status_code=404, detail="Respuesta no encontrada")
    
    # Validar que la pregunta existe
    question = db.query(Question).filter(Question.id == payload.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    
    # Validar que respuesta_seleccionada está en rango válido
    opciones_list = cast(list[str], question.opciones) if isinstance(question.opciones, list) else []
    if not (0 <= payload.respuesta_seleccionada < len(opciones_list)):
        raise HTTPException(
            status_code=400,
            detail=f"respuesta_seleccionada debe estar entre 0 y {len(opciones_list) - 1}"
        )
    
    # Actualizar respuesta
    answer.respuesta_seleccionada = payload.respuesta_seleccionada  # type: ignore
    answer.es_correcta = (payload.respuesta_seleccionada == question.respuesta_correcta)  # type: ignore
    answer.tiempo_respuesta_segundos = payload.tiempo_respuesta_segundos  # type: ignore
    
    db.add(answer)
    db.commit()
    db.refresh(answer)
    return answer
