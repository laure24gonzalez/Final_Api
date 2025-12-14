"""
Servicios de negocio para operaciones de quiz
"""
from sqlalchemy.orm import Session
from ..models.question import Question
from ..models.answer import Answer
from ..models.quiz_session import QuizSession


def validate_question_data(pregunta: str, opciones: list, respuesta_correcta: int, categoria: str, dificultad: str):
    """
    Validar datos de una pregunta
    
    Args:
        pregunta: Texto de la pregunta
        opciones: Lista de opciones (debe tener 3-5 elementos)
        respuesta_correcta: Índice de la respuesta correcta
        categoria: Categoría de la pregunta
        dificultad: Nivel de dificultad
    
    Raises:
        ValueError: Si los datos no son válidos
    """
    if not (3 <= len(opciones) <= 5):
        raise ValueError("Debe haber entre 3 y 5 opciones")
    
    if not (0 <= respuesta_correcta < len(opciones)):
        raise ValueError(f"respuesta_correcta debe estar entre 0 y {len(opciones) - 1}")
    
    valid_categories = ["Tecnología", "Historia", "Ciencia", "Geografía", "Literatura", "Deporte"]
    if categoria not in valid_categories:
        raise ValueError(f"Categoría debe ser una de: {', '.join(valid_categories)}")
    
    valid_levels = ["fácil", "medio", "difícil"]
    if dificultad not in valid_levels:
        raise ValueError(f"Dificultad debe ser una de: {', '.join(valid_levels)}")


def _normalize_text(s: str) -> str:
    import unicodedata
    if not s:
        return ""
    s = s.strip().lower()
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    return s


CANONICAL_CATEGORIES = ["Tecnología", "Historia", "Ciencia", "Geografía", "Literatura", "Deporte"]
CANONICAL_DIFFICULTIES = ["fácil", "medio", "difícil"]


_CATEGORY_MAP = { _normalize_text(c): c for c in CANONICAL_CATEGORIES }
_DIFFICULTY_MAP = { _normalize_text(d): d for d in CANONICAL_DIFFICULTIES }


def canonical_category(value: str) -> str:
    """Map input to a canonical category (accent- and case-insensitive).

    Returns canonical string or raises ValueError if unknown.
    """
    if value is None:
        return None
    key = _normalize_text(value)
    if key in _CATEGORY_MAP:
        return _CATEGORY_MAP[key]
    raise ValueError(f"Categoría debe ser una de: {', '.join(CANONICAL_CATEGORIES)}")


def canonical_difficulty(value: str) -> str:
    if value is None:
        return None
    key = _normalize_text(value)
    if key in _DIFFICULTY_MAP:
        return _DIFFICULTY_MAP[key]
    raise ValueError(f"Dificultad debe ser una de: {', '.join(CANONICAL_DIFFICULTIES)}")


def calculate_session_score(session: QuizSession, db: Session) -> tuple:
    """
    Calcular la puntuación de una sesión basada en sus respuestas
    
    Args:
        session: Sesión de quiz
        db: Sesión de base de datos
    
    Returns:
        Tupla (puntuacion_total, preguntas_respondidas, preguntas_correctas, tiempo_total)
    """
    answers = db.query(Answer).filter(Answer.quiz_session_id == session.id).all()
    
    preguntas_respondidas = len(answers)
    preguntas_correctas = sum(1 for a in answers if a.es_correcta)
    tiempo_total = sum(a.tiempo_respuesta_segundos for a in answers if a.tiempo_respuesta_segundos)
    
    # Calcular puntuación como porcentaje
    puntuacion = (preguntas_correctas * 100 // preguntas_respondidas) if preguntas_respondidas > 0 else 0
    
    return puntuacion, preguntas_respondidas, preguntas_correctas, tiempo_total if tiempo_total > 0 else None


def get_question_statistics(question_id: int, db: Session) -> dict:
    """
    Obtener estadísticas de una pregunta específica
    
    Args:
        question_id: ID de la pregunta
        db: Sesión de base de datos
    
    Returns:
        Diccionario con estadísticas
    """
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        return {}
    
    answers = db.query(Answer).filter(Answer.question_id == question_id).all()
    total = len(answers)
    correctas = sum(1 for a in answers if a.es_correcta)
    tasa_acierto = (correctas / total * 100) if total > 0 else 0
    
    return {
        "question_id": question_id,
        "pregunta": question.pregunta,
        "categoria": question.categoria,
        "dificultad": question.dificultad,
        "veces_respondida": total,
        "veces_correcta": correctas,
        "tasa_acierto": round(tasa_acierto, 2)
    }


def get_category_statistics(categoria: str, db: Session) -> dict:
    """
    Obtener estadísticas de una categoría
    
    Args:
        categoria: Nombre de la categoría
        db: Sesión de base de datos
    
    Returns:
        Diccionario con estadísticas
    """
    preguntas = db.query(Question).filter(
        Question.categoria == categoria,
        Question.is_active == True
    ).all()
    
    preguntas_ids = [p.id for p in preguntas]
    if not preguntas_ids:
        return {}
    
    answers = db.query(Answer).filter(Answer.question_id.in_(preguntas_ids)).all()
    total = len(answers)
    correctas = sum(1 for a in answers if a.es_correcta)
    promedio_aciertos = (correctas / total * 100) if total > 0 else 0
    
    return {
        "categoria": categoria,
        "num_preguntas": len(preguntas_ids),
        "num_respuestas": total,
        "aciertos": correctas,
        "promedio_aciertos": round(promedio_aciertos, 2)
    }

