import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html
from .database import Base, engine
from .routers import students, grades

@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(engine)
    yield

app = FastAPI(title="Студенческий журнал", version="1.0.0", description="Лабораторная работа №1. Вариант 2.", lifespan=lifespan, redoc_url=None)
app.add_middleware(CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(","),
    allow_methods=["GET", "POST", "PUT", "DELETE"], allow_headers=["Content-Type"])
app.include_router(students.router, prefix="/api")
app.include_router(grades.router, prefix="/api")

@app.get("/api/health", tags=["Система"])
def health():
    return {"status": "ok"}


@app.get("/redoc", include_in_schema=False)
def redoc_documentation():
    # Pin the classic bundle: the moving @next bundle uses module-only syntax.
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.5.4/bundles/redoc.standalone.js",
        with_google_fonts=False,
    )
