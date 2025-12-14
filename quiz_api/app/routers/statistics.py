from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
from ..database import get_db
from ..models.quiz_session import QuizSession
from ..models.answer import Answer
from ..models.question import Question

router = APIRouter()


@router.get("/global")
def statistics_global(db: Session = Depends(get_db)):
    """
    Obtener estadísticas globales del sistema.
    
    Retorna:
    - Total de preguntas activas en el sistema
    - Total de sesiones completadas
    - Promedio de aciertos general (de todas las sesiones)
    - Categorías con mayor tasa de error (top 5)
    
    Útil para dashboards y análisis del rendimiento global.
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        dict: Diccionario con estadísticas globales
    """
    # Total de preguntas activas
    total_preguntas = db.query(func.count(Question.id)).filter(Question.is_active == True).scalar()
    
    # Total de sesiones completadas
    total_sesiones = db.query(func.count(QuizSession.id)).filter(QuizSession.estado == "completado").scalar()
    
    # Promedio de aciertos general
    sesiones = db.query(QuizSession).filter(QuizSession.estado == "completado").all()
    promedio_aciertos = (
        sum(s.puntuacion_total for s in sesiones) / len(sesiones)
        if sesiones else 0
    )
    
    # Categorías más difíciles (con mayor tasa de error)
    categorias_query = db.query(Question.categoria).filter(Question.is_active == True).distinct().all()
    categorias_dificiles = []
    
    for (cat,) in categorias_query:
        preguntas_cat = db.query(Question.id).filter(Question.categoria == cat, Question.is_active == True).all()
        preguntas_ids = [p[0] for p in preguntas_cat]
        
        if preguntas_ids:
            answers_cat = db.query(Answer).filter(Answer.question_id.in_(preguntas_ids)).all()
            total_resp = len(answers_cat)
            correctas = sum(1 for a in answers_cat if a.es_correcta)
            tasa_error = ((total_resp - correctas) / total_resp * 100) if total_resp > 0 else 0
            categorias_dificiles.append({
                "categoria": cat,
                "tasa_error": round(tasa_error, 2)
            })
    
    categorias_dificiles.sort(key=lambda x: x["tasa_error"], reverse=True)
    
    return {
        "total_preguntas_activas": total_preguntas,
        "total_sesiones_completadas": total_sesiones,
        "promedio_aciertos": round(promedio_aciertos, 2),
        "categorias_dificiles": categorias_dificiles[:5]
    }


@router.get("/session/{session_id}")
def statistics_session(session_id: int, db: Session = Depends(get_db)):
    """
    Obtener estadísticas detalladas de una sesión específica.
    
    Incluye:
    - Puntuación final y porcentaje de aciertos
    - Número de preguntas respondidas y correctas
    - Tiempo promedio y total por pregunta
    - Resumen detallado de cada respuesta (pregunta, opción seleccionada, si fue correcta)
    
    Útil para mostrar resultados finales después de completar un quiz.
    
    Args:
        session_id: ID de la sesión
        db: Sesión de base de datos
        
    Returns:
        dict: Diccionario con estadísticas completas de la sesión
        
    Raises:
        HTTPException: Si la sesión no existe (404)
    """
    session = db.query(QuizSession).filter(QuizSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    # Obtener respuestas
    answers = db.query(Answer).filter(Answer.quiz_session_id == session_id).all()
    
    # Calcular estadísticas
    total_respondidas = len(answers)
    correctas = sum(1 for a in answers if a.es_correcta)
    porcentaje_aciertos = (correctas / total_respondidas * 100) if total_respondidas > 0 else 0
    
    tiempo_promedio = None
    if answers and any(a.tiempo_respuesta_segundos for a in answers):
        tiempos = [a.tiempo_respuesta_segundos for a in answers if a.tiempo_respuesta_segundos]
        tiempo_promedio = sum(tiempos) / len(tiempos) if tiempos else None
    
    # Resumen detallado de respuestas
    resumen_respuestas = []
    for answer in answers:
        question = db.query(Question).filter(Question.id == answer.question_id).first()
        resumen_respuestas.append({
            "question_id": answer.question_id,
            "pregunta": question.pregunta if question else None,
            "respuesta_seleccionada": answer.respuesta_seleccionada,
            "es_correcta": answer.es_correcta,
            "tiempo_segundos": answer.tiempo_respuesta_segundos
        })
    
    return {
        "session_id": session_id,
        "usuario": session.usuario_nombre,
        "puntuacion_final": session.puntuacion_total,
        "porcentaje_aciertos": round(porcentaje_aciertos, 2),
        "preguntas_respondidas": total_respondidas,
        "preguntas_correctas": correctas,
        "tiempo_promedio_segundos": round(tiempo_promedio, 2) if tiempo_promedio else None,
        "tiempo_total_segundos": session.tiempo_total_segundos,
        "resumen_respuestas": resumen_respuestas
    }


@router.get("/questions/difficult")
def statistics_difficult_questions(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Obtener las preguntas con mayor tasa de error.
    
    Retorna un listado de preguntas ordenadas por tasa de error (de mayor a menor),
    incluyendo cuántas veces fueron respondidas y cuántas veces incorrectamente.
    
    Útil para identificar preguntas que necesitan revisión o aclaración.
    
    Args:
        db: Sesión de base de datos
        limit: Número máximo de preguntas a retornar (1-50, default: 10)
        
    Returns:
        List[dict]: Lista de preguntas con sus tasas de error
    """
    preguntas = db.query(Question).filter(Question.is_active == True).all()
    
    preguntas_dificiles = []
    for q in preguntas:
        answers = db.query(Answer).filter(Answer.question_id == q.id).all()
        if answers:
            total = len(answers)
            incorrectas = sum(1 for a in answers if not a.es_correcta)
            tasa_error = (incorrectas / total * 100)
            preguntas_dificiles.append({
                "question_id": q.id,
                "pregunta": q.pregunta,
                "categoria": q.categoria,
                "dificultad": q.dificultad,
                "veces_respondida": total,
                "veces_incorrecta": incorrectas,
                "tasa_error": round(tasa_error, 2)
            })
    
    preguntas_dificiles.sort(key=lambda x: x["tasa_error"], reverse=True)
    return preguntas_dificiles[:limit]


@router.get("/categories")
def statistics_by_categories(db: Session = Depends(get_db)):
    """
    Obtener rendimiento de los usuarios por categoría de pregunta.
    
    Retorna:
    - Para cada categoría: número de preguntas, total de respuestas, aciertos y promedio
    - Ordenado de mayor a menor por promedio de aciertos
    
    Útil para identificar en qué temas los usuarios tienen mejor/peor rendimiento.
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        List[dict]: Lista de categorías con sus estadísticas de rendimiento
    """
    categorias = db.query(Question.categoria).filter(Question.is_active == True).distinct().all()
    
    rendimiento = []
    for (categoria,) in categorias:
        preguntas = db.query(Question.id).filter(Question.categoria == categoria, Question.is_active == True).all()
        preguntas_ids = [p[0] for p in preguntas]
        
        if preguntas_ids:
            answers = db.query(Answer).filter(Answer.question_id.in_(preguntas_ids)).all()
            total = len(answers)
            correctas = sum(1 for a in answers if a.es_correcta)
            promedio_aciertos = (correctas / total * 100) if total > 0 else 0
            
            rendimiento.append({
                "categoria": categoria,
                "num_preguntas": len(preguntas_ids),
                "num_respuestas": total,
                "aciertos": correctas,
                "promedio_aciertos": round(promedio_aciertos, 2)
            })
    
    rendimiento.sort(key=lambda x: x["promedio_aciertos"], reverse=True)
    return rendimiento
