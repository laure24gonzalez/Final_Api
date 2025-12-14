"""Script para cargar datos de prueba en la base de datos"""
import sys
import os
from typing import Any, cast

if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"

from app.database import SessionLocal, Base, engine
from app.models.question import Question
from app.models.quiz_session import QuizSession
from app.models.answer import Answer
from datetime import datetime, timedelta, timezone


def seed_data(force: bool = False) -> None:
    # Carga datos de prueba en la BD
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing = db.query(Question).first()
        if existing and not force:
            print("[INFO] La base de datos ya contiene datos. Saltando seed...")
            return

        if force:
            print("[INFO] Force seed enabled: limpiando tablas...")
            db.query(Answer).delete()
            db.query(QuizSession).delete()
            db.query(Question).delete()
            db.commit()

        preguntas: list[dict[str, Any]] = [
        # Tecnología
        {
            "pregunta": "¿Qué es FastAPI?",
            "opciones": ["Una base de datos", "Un framework web", "Un lenguaje de programación", "Un editor de código"],
            "respuesta_correcta": 1,
            "explicacion": "FastAPI es un framework web moderno y rápido para construir APIs REST con Python",
            "categoria": "Tecnología",
            "dificultad": "fácil"
        },
        {
            "pregunta": "¿Cuál es la complejidad temporal de una búsqueda binaria?",
            "opciones": ["O(n)", "O(n²)", "O(log n)", "O(n log n)"],
            "respuesta_correcta": 2,
            "explicacion": "La búsqueda binaria tiene complejidad O(log n) porque divide el problema por la mitad en cada iteración",
            "categoria": "Tecnología",
            "dificultad": "medio"
        },
        {
            "pregunta": "¿Qué es SQLAlchemy?",
            "opciones": ["Un gestor de paquetes", "Un ORM de Python", "Un servidor web", "Una base de datos"],
            "respuesta_correcta": 1,
            "explicacion": "SQLAlchemy es un ORM (Object-Relational Mapping) para Python que facilita el trabajo con bases de datos",
            "categoria": "Tecnología",
            "dificultad": "fácil"
        },
        {
            "pregunta": "¿Cuál de los siguientes NO es un tipo de dato en Python?",
            "opciones": ["list", "tuple", "array", "dict"],
            "respuesta_correcta": 2,
            "explicacion": "array no es un tipo de dato nativo de Python, aunque existe en la librería array y numpy",
            "categoria": "Tecnología",
            "dificultad": "medio"
        },
        {
            "pregunta": "¿Qué significa CORS?",
            "opciones": ["Cross-Origin Request System", "Cross-Origin Resource Sharing", "Cross-Object Request Support", "Coordinated Origin Resource System"],
            "respuesta_correcta": 1,
            "explicacion": "CORS (Cross-Origin Resource Sharing) permite que recursos de un dominio accedan a recursos de otro dominio",
            "categoria": "Tecnología",
            "dificultad": "difícil"
        },
        # Historia
        {
            "pregunta": "¿En qué año cayó el Muro de Berlín?",
            "opciones": ["1987", "1989", "1991", "1993"],
            "respuesta_correcta": 1,
            "explicacion": "El Muro de Berlín cayó el 9 de noviembre de 1989, marcando el fin de la Guerra Fría",
            "categoria": "Historia",
            "dificultad": "medio"
        },
        {
            "pregunta": "¿Quién fue el primer presidente de los Estados Unidos?",
            "opciones": ["Thomas Jefferson", "George Washington", "John Adams", "Benjamin Franklin"],
            "respuesta_correcta": 1,
            "explicacion": "George Washington fue el primer presidente de los Estados Unidos (1789-1797)",
            "categoria": "Historia",
            "dificultad": "fácil"
        },
        {
            "pregunta": "¿En qué siglo ocurrió la Revolución Francesa?",
            "opciones": ["Siglo XVII", "Siglo XVIII", "Siglo XIX", "Siglo XX"],
            "respuesta_correcta": 1,
            "explicacion": "La Revolución Francesa ocurrió principalmente en el siglo XVIII (1789-1799)",
            "categoria": "Historia",
            "dificultad": "medio"
        },
        {
            "pregunta": "¿Cuál fue el imperio más grande de la historia?",
            "opciones": ["Imperio Otomano", "Imperio Español", "Imperio Británico", "Imperio Romano"],
            "respuesta_correcta": 2,
            "explicacion": "El Imperio Británico fue el más grande en términos de territorio y población que gobernaba",
            "categoria": "Historia",
            "dificultad": "difícil"
        },
        {
            "pregunta": "¿En qué año terminó la Segunda Guerra Mundial?",
            "opciones": ["1943", "1944", "1945", "1946"],
            "respuesta_correcta": 2,
            "explicacion": "La Segunda Guerra Mundial terminó en 1945, con la rendición de Japón el 2 de septiembre",
            "categoria": "Historia",
            "dificultad": "fácil"
        },
        # Ciencia
        {
            "pregunta": "¿Cuál es el elemento químico más abundante en el universo?",
            "opciones": ["Oxígeno", "Helio", "Hidrógeno", "Carbono"],
            "respuesta_correcta": 2,
            "explicacion": "El hidrógeno es el elemento más abundante en el universo, formando la mayoría de las estrellas",
            "categoria": "Ciencia",
            "dificultad": "medio"
        },
        {
            "pregunta": "¿A cuántos grados Celsius hierve el agua al nivel del mar?",
            "opciones": ["90°C", "100°C", "110°C", "120°C"],
            "respuesta_correcta": 1,
            "explicacion": "El agua hierve a 100°C al nivel del mar (a una presión de 1 atmósfera)",
            "categoria": "Ciencia",
            "dificultad": "fácil"
        },
        {
            "pregunta": "¿Cuál es la velocidad de la luz en el vacío?",
            "opciones": ["200,000 km/s", "300,000 km/s", "400,000 km/s", "500,000 km/s"],
            "respuesta_correcta": 1,
            "explicacion": "La velocidad de la luz es aproximadamente 300,000 km/s o 3×10⁸ m/s",
            "categoria": "Ciencia",
            "dificultad": "medio"
        },
        {
            "pregunta": "¿Cuántos cromosomas tiene un ser humano?",
            "opciones": ["23", "46", "92", "184"],
            "respuesta_correcta": 1,
            "explicacion": "Los seres humanos tenemos 46 cromosomas (23 pares), 23 de cada progenitor",
            "categoria": "Ciencia",
            "dificultad": "medio"
        },
        {
            "pregunta": "¿Cuál es la unidad básica de la vida?",
            "opciones": ["Átomo", "Molécula", "Célula", "Tejido"],
            "respuesta_correcta": 2,
            "explicacion": "La célula es la unidad básica de la vida; todos los organismos vivos están compuestos de células",
            "categoria": "Ciencia",
            "dificultad": "fácil"
        },
        # Geografía
        {
            "pregunta": "¿Cuál es la capital de Francia?",
            "opciones": ["Lyon", "Marsella", "París", "Toulouse"],
            "respuesta_correcta": 2,
            "explicacion": "París es la capital y ciudad más grande de Francia",
            "categoria": "Geografía",
            "dificultad": "fácil"
        },
        {
            "pregunta": "¿Cuál es el río más largo del mundo?",
            "opciones": ["Amazonas", "Nilo", "Yangtsé", "Misisipi"],
            "respuesta_correcta": 1,
            "explicacion": "El río Nilo es el río más largo del mundo, con aproximadamente 6,650 km de longitud",
            "categoria": "Geografía",
            "dificultad": "medio"
        }
    ]
        
        questions_db: list[Question] = []
        for p in preguntas:
            opciones: Any = p.get("opciones", [])
            resp_idx: Any = p.get("respuesta_correcta")
            if not isinstance(opciones, list) or not (3 <= len(opciones) <= 5):  # type: ignore
                print(f"[WARN] Pregunta inválida (opciones): {p.get('pregunta')}. Se requieren 3-5 opciones. Saltando.")
                continue
            if not isinstance(resp_idx, int) or resp_idx < 0 or resp_idx >= len(opciones):  # type: ignore
                print(f"[WARN] Pregunta inválida (respuesta_correcta fuera de rango): {p.get('pregunta')}. Saltando.")
                continue

            q = Question(
                pregunta=p["pregunta"],
                opciones=opciones,
                respuesta_correcta=resp_idx,
                explicacion=p.get("explicacion"),
                categoria=p.get("categoria", "General"),
                dificultad=p.get("dificultad", "medio"),
                is_active=True,
            )
            db.add(q)
            questions_db.append(q)
        
        db.commit()

        # Crea sesiones de ejemplo
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        sesiones: list[dict[str, Any]] = [
        {
            "usuario_nombre": "Juan Pérez",
            "fecha_inicio": now - timedelta(days=3),
            "fecha_fin": now - timedelta(days=3, hours=1),
            "preguntas": [0, 1, 2, 3, 4],
            "respuestas": [1, 2, 1, 2, 1]
        },
        {
            "usuario_nombre": "María García",
            "fecha_inicio": now - timedelta(days=2),
            "fecha_fin": now - timedelta(days=2, hours=1),
            "preguntas": [5, 6, 7, 8, 9],
            "respuestas": [1, 1, 1, 2, 2]
        },
        {
            "usuario_nombre": "Carlos López",
            "fecha_inicio": now - timedelta(days=1),
            "fecha_fin": now - timedelta(days=1, hours=1),
            "preguntas": [10, 11, 12, 13, 14],
            "respuestas": [2, 1, 1, 1, 2]
        }
    ]
    
        for s_data in sesiones:
            session = QuizSession(
                usuario_nombre=s_data["usuario_nombre"],
                fecha_inicio=s_data["fecha_inicio"],
                fecha_fin=s_data["fecha_fin"],
                estado="completado"
            )
            db.add(session)
            db.flush()

            correctas: int = 0
            tiempo_total: int = 0
            for q_idx, respuesta in zip(s_data["preguntas"], s_data["respuestas"]):
                if q_idx < 0 or q_idx >= len(questions_db):
                    print(f"[WARN] Índice de pregunta fuera de rango: {q_idx}. Saltando respuesta.")
                    continue

                question = cast(Question, questions_db[q_idx])
                es_correcta: bool = (respuesta == question.respuesta_correcta)
                if es_correcta:
                    correctas += 1

                tiempo_respuesta: int = 10 + (q_idx % 5) * 3
                tiempo_total += tiempo_respuesta

                answer = Answer(
                    quiz_session_id=session.id,
                    question_id=question.id,
                    respuesta_seleccionada=respuesta,
                    es_correcta=es_correcta,
                    tiempo_respuesta_segundos=tiempo_respuesta,
                )
                db.add(answer)

            preguntas_respondidas: int = len([q for q in s_data["preguntas"] if 0 <= q < len(questions_db)])
            puntuacion: int = (correctas * 100 // preguntas_respondidas) if preguntas_respondidas > 0 else 0

            session.preguntas_respondidas = preguntas_respondidas  # type: ignore
            session.preguntas_correctas = correctas  # type: ignore
            session.puntuacion_total = puntuacion  # type: ignore
            session.tiempo_total_segundos = tiempo_total  # type: ignore

            db.add(session)

        db.commit()
        print(f"✓ Datos cargados: {len(preguntas)} preguntas, {len(sesiones)} sesiones")
    except Exception as exc:
        db.rollback()
        print(f"Error cargando datos: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Cargar datos de prueba en la base de datos")
    parser.add_argument('--force', action='store_true', help='Forzar limpieza y volver a sembrar')
    args = parser.parse_args()

    seed_data(force=args.force)
