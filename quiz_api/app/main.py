from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from .database import engine, Base
from .routers import questions, quiz_sessions, answers, statistics


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("✓ BD inicializada")
    
    if os.getenv("SEED_ON_STARTUP", "").lower() in ("1", "true", "yes"):
        force = os.getenv("SEED_FORCE", "").lower() in ("1", "true", "yes")
        try:
            from .seed_data import seed_data
            seed_data(force=force)
        except Exception as exc:
            print(f"[WARN] Error en siembra automática: {exc}")
    
    yield
    print("✓ Aplicación detenida")


app = FastAPI(
    title="Quiz API",
    description="API REST completa para un quiz interactivo",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(questions.router, prefix="/questions", tags=["Questions"])
app.include_router(quiz_sessions.router, prefix="/quiz-sessions", tags=["Quiz Sessions"])
app.include_router(answers.router, prefix="/answers", tags=["Answers"])
app.include_router(statistics.router, prefix="/statistics", tags=["Statistics"])
