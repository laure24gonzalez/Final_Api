# Quiz API 📚

Un sitio para hacer quizzes. Tiene una API en FastAPI, base de datos en SQLite, y una interfaz web para poder usar el sitio.

## Qué se puede hacer

- Crear, editar y eliminar preguntas
- Hacer quizzes y ver cuántas acertaste
- Ver estadísticas de cuál fue tu desempeño
- Guardar el historial de quizzes que hiciste
- Filtrar preguntas por categoría y dificultad
- Ver qué preguntas son las más difíciles

## Estructura del Proyecto

```
quiz_api/
├── app/
│   ├── main.py                 # El punto de entrada
│   ├── database.py             # Conexión a la BD
│   ├── seed_data.py            # Carga los datos de ejemplo
│   ├── models/
│   │   ├── question.py         # La tabla de preguntas
│   │   ├── quiz_session.py     # La tabla de sesiones
│   │   └── answer.py           # La tabla de respuestas
│   ├── schemas/
│   │   ├── question.py
│   │   ├── quiz_session.py
│   │   └── answer.py
│   ├── routers/
│   │   ├── questions.py        # Los endpoints de preguntas
│   │   ├── quiz_sessions.py    # Los endpoints de sesiones
│   │   ├── answers.py          # Los endpoints de respuestas
│   │   └── statistics.py       # Los endpoints de estadísticas
│   └── services/
│       └── quiz_service.py     # Funciones auxiliares
├── static/
│   ├── index.html              # El HTML del sitio
│   ├── styles.css              # Los estilos
│   └── script.js               # El código JavaScript
├── requirements.txt
├── serve_static.py             # Servidor del frontend
└── README.md
```

## Cómo instalar

### Paso 1: Entorno virtual

**En Windows:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**En Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

### Paso 2: Instalar librerías

```bash
pip install -r requirements.txt
```

### Paso 3: Correr la API

```bash
cd quiz_api
uvicorn app.main:app --reload
```

Abre otra terminal y haz:

### Paso 4: Correr el frontend

```bash
cd quiz_api
python serve_static.py
```

### Dónde verlo

- El sitio está en: http://localhost:3000
- La API en: http://localhost:8000
- Documentación en: http://localhost:8000/docs

## Las secciones del sitio

### 1. Inicio
Es la página principal, con un saludo y botones para ir a las otras secciones.

### 2. Tomar Quiz
Acá podés hacer un quiz. Elegís cuántas preguntas querés responder, y después respondés cada una. Al final te dice cuántas acertaste.

### 3. Crear Pregunta
Un formulario para agregar nuevas preguntas. Tenés que poner:
- La pregunta
- 4 opciones de respuesta
- Cuál es la opción correcta
- La categoría (Tecnología, Historia, etc.)
- Si es fácil, medio o difícil
- Una explicación (opcional)

### 4. Gestión de Preguntas
Acá ves todas las preguntas que existen. Podés:
- Filtrarlas por categoría o dificultad
- Buscar una pregunta específica
- Editar una pregunta que ya existe
- Eliminar una pregunta

### 5. Estadísticas
Te muestra datos sobre cómo fue tu desempeño:
- Cuántas preguntas hay en total
- Cuántos quizzes completaste
- En promedio, cuánta puntuación sacas
- Qué preguntas son las más difíciles
- Cómo te va en cada categoría

### 6. Sesiones
Es el historial de todos los quizzes que hiciste. Podés ver cuándo los hiciste y cuánto sacaste en cada uno.

## Cómo está hecho por dentro

### Las tablas de la BD

**Preguntas (Question)**
- id
- pregunta: el texto de la pregunta
- opciones: las 4 opciones posibles
- respuesta_correcta: cuál es la respuesta correcta
- categoría: en qué tema va
- dificultad: fácil, medio o difícil

**Sesiones de Quiz (QuizSession)**
- id
- usuario_nombre: quién hizo el quiz
- fecha: cuándo lo hizo
- puntuación: cuánto sacó
- estado: si ya terminó o está en progreso

**Respuestas (Answer)**
- id
- session_id: de qué sesión es
- question_id: qué pregunta respondió
- respuesta_seleccionada: qué opción eligió
- es_correcta: si acertó o no

## Los endpoints principales

### Para preguntas
- `POST /questions/` - Crear pregunta
- `GET /questions/` - Ver todas las preguntas
- `GET /questions/{id}` - Ver una pregunta específica
- `PUT /questions/{id}` - Editar pregunta
- `DELETE /questions/{id}` - Eliminar pregunta
- `GET /questions/random?limit=5` - Obtener 5 preguntas al azar

### Para quizzes
- `POST /quiz-sessions/` - Empezar un quiz
- `GET /quiz-sessions/` - Ver todos los quizzes que hiciste
- `PUT /quiz-sessions/{id}/complete` - Terminar un quiz

### Para respuestas
- `POST /answers/` - Registrar una respuesta
- `GET /answers/session/{id}` - Ver todas las respuestas de un quiz

### Para estadísticas
- `GET /statistics/global` - Estadísticas generales
- `GET /statistics/session/{id}` - Stats de un quiz específico
- `GET /statistics/questions/difficult` - Qué preguntas la gente no acuella
- `GET /statistics/categories` - Cómo te va en cada tema

## Validaciones

Las categorías válidas son: Tecnología, Historia, Ciencia, Geografía, Literatura, Deporte

Las dificultades son: fácil, medio, difícil

Cada pregunta debe tener entre 3 y 5 opciones.

## Tecnologías que usé

**Backend:**
- FastAPI (el framework para la API)
- SQLAlchemy (para conectar con la BD)
- SQLite (la base de datos)
- Pydantic (para validar datos)
- Uvicorn (el servidor)

**Frontend:**
- HTML5
- CSS3 (con diseño responsivo)
- JavaScript vanilla (sin jQuery ni nada raro)

## Datos de ejemplo

Viene con 17 preguntas de ejemplo:
- 5 de Tecnología
- 5 de Historia
- 3 de Ciencia
- 2 de Geografía
- 1 de Literatura
- 1 de Deporte

Con distintos niveles de dificultad (fácil, medio, difícil).

## Problemas que pueden pasar

**No funciona la conexión entre el sitio y la API**
- Verificar que estén corriendo los dos servidores (puerto 8000 y 3000)
- Mirar la consola del navegador (F12) para ver si hay errores

**No aparecen las preguntas**
- Eliminar el archivo `quiz.db` y correr la API de nuevo
- Que se ejecute automáticamente el archivo que carga los datos

**No puedo editar una pregunta**
- Verificar que la pregunta todavía exista
- Usar el número de ID correcto

