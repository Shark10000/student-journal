import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routers import students, grades

@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(engine)
    yield

app = FastAPI(title="Студенческий журнал", version="1.0.0", description="Лабораторная работа №1. Вариант 2.", lifespan=lifespan)
app.add_middleware(CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(","),
    allow_methods=["GET", "POST", "PUT", "DELETE"], allow_headers=["Content-Type"])
app.include_router(students.router, prefix="/api")
app.include_router(grades.router, prefix="/api")

@app.get("/api/health", tags=["Система"])
def health():
    return {"status": "ok"}
