from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from random import sample
from ..database import get_db
from ..models.question import Question
from ..schemas.question import QuestionCreate, QuestionRead

# Type hints for better IDE support
QuestionList = List[QuestionRead]

router = APIRouter()


@router.post("/", response_model=QuestionRead)
def create_question(payload: QuestionCreate, db: Session = Depends(get_db)):
    """
    Crear una nueva pregunta con validaciones.
    
    - Valida que haya entre 3 y 5 opciones
    - Valida que respuesta_correcta esté dentro del rango válido
    - Valida que categoría y dificultad sean válidas
    
    Args:
        payload: Datos de la pregunta a crear
        db: Sesión de base de datos
        
    Returns:
        QuestionRead: Pregunta creada con su ID
    """
    q = Question(
        pregunta=payload.pregunta,
        opciones=payload.opciones,
        respuesta_correcta=payload.respuesta_correcta,
        explicacion=payload.explicacion,
        categoria=payload.categoria,
        dificultad=payload.dificultad
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


@router.get("/random", response_model=List[QuestionRead])
def get_random_questions(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Obtener preguntas aleatorias para un quiz.
    
    Este endpoint retorna un número aleatorio de preguntas activas.
    Útil para iniciar una sesión de quiz con preguntas variadas.
    
    Args:
        db: Sesión de base de datos
        limit: Número máximo de preguntas a retornar (1-50, default: 10)
        
    Returns:
        List[QuestionRead]: Lista de preguntas aleatorias
        
    Raises:
        HTTPException: Si no hay preguntas disponibles
    """
    total = db.query(func.count(Question.id)).filter(Question.is_active == True).scalar()
    if total == 0:
        raise HTTPException(status_code=404, detail="No hay preguntas disponibles")
    
    num_questions = min(limit, total)
    questions = db.query(Question).filter(Question.is_active == True).all()
    return sample(questions, num_questions)


@router.get("/", response_model=List[QuestionRead])
def list_questions(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    categoria: str = Query(None),
    dificultad: str = Query(None),
    is_active: bool = Query(True)
):
    """
    Listar preguntas activas con filtros y paginación.
    
    Args:
        db: Sesión de base de datos
        skip: Número de registros a saltar (default: 0)
        limit: Número máximo de registros a retornar (1-100, default: 10)
        categoria: Filtrar por categoría (opcional)
        dificultad: Filtrar por dificultad (opcional)
        is_active: Filtrar por estado activo (default: True)
        
    Returns:
        List[QuestionRead]: Lista de preguntas que cumplen los filtros
    """
    query = db.query(Question).filter(Question.is_active == is_active)
    
    if categoria:
        query = query.filter(Question.categoria == categoria)
    if dificultad:
        query = query.filter(Question.dificultad == dificultad)
    
    return query.offset(skip).limit(limit).all()


@router.get("/{question_id}", response_model=QuestionRead)
def get_question(question_id: int, db: Session = Depends(get_db)):
    """
    Obtener una pregunta específica por ID.
    
    Args:
        question_id: ID de la pregunta a obtener
        db: Sesión de base de datos
        
    Returns:
        QuestionRead: Datos completos de la pregunta
        
    Raises:
        HTTPException: Si la pregunta no existe (404)
    """
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    return q


@router.put("/{question_id}", response_model=QuestionRead)
def update_question(
    question_id: int,
    payload: QuestionCreate,
    db: Session = Depends(get_db)
) -> QuestionRead:
    """
    Actualizar una pregunta existente.
    
    Permite modificar todos los campos de una pregunta.
    Las validaciones de Pydantic se aplican al payload.
    
    Args:
        question_id: ID de la pregunta a actualizar
        payload: Nuevos datos de la pregunta
        db: Sesión de base de datos
        
    Returns:
        QuestionRead: Pregunta actualizada
        
    Raises:
        HTTPException: Si la pregunta no existe (404)
    """
    q: Question | None = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    
    q.pregunta = payload.pregunta  # type: ignore
    q.opciones = payload.opciones  # type: ignore
    q.respuesta_correcta = payload.respuesta_correcta  # type: ignore
    q.explicacion = payload.explicacion  # type: ignore
    q.categoria = payload.categoria  # type: ignore
    q.dificultad = payload.dificultad  # type: ignore
    
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


@router.delete("/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    """
    Eliminar una pregunta (soft delete).
    
    No elimina la pregunta de la base de datos, solo marca is_active como False.
    Esto preserva la integridad referencial con las respuestas ya registradas.
    
    Args:
        question_id: ID de la pregunta a eliminar
        db: Sesión de base de datos
        
    Returns:
        dict: Mensaje de confirmación
        
    Raises:
        HTTPException: Si la pregunta no existe (404)
    """
    q: Question | None = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    
    q.is_active = False  # type: ignore
    db.add(q)
    db.commit()
    return {"detail": "Pregunta eliminada"}


@router.post("/bulk", response_model=List[QuestionRead])
def bulk_create_questions(
    payload: List[QuestionCreate],
    db: Session = Depends(get_db)
) -> List[QuestionRead]:
    """
    Crear múltiples preguntas desde JSON en una sola petición.
    
    Útil para cargar un conjunto de preguntas desde un archivo JSON.
    Todas las validaciones de Pydantic se aplican a cada pregunta.
    
    Args:
        payload: Lista de preguntas a crear
        db: Sesión de base de datos
        
    Returns:
        List[QuestionRead]: Lista de preguntas creadas con sus IDs
        
    Raises:
        HTTPException: Si alguna pregunta contiene datos inválidos (400)
    """
    questions: list[Question] = []
    for item in payload:
        q = Question(
            pregunta=item.pregunta,
            opciones=item.opciones,
            respuesta_correcta=item.respuesta_correcta,
            explicacion=item.explicacion,
            categoria=item.categoria,
            dificultad=item.dificultad
        )
        db.add(q)
        questions.append(q)
    
    db.commit()
    for q in questions:
        db.refresh(q)
    
    return questions  # type: ignore
