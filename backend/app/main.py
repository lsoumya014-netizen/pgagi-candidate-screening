import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .config import settings, PROJECT_ROOT
from .models.database import init_db
from .services.rag_engine import rag_engine
from .api.interview import router as interview_router
from .api.reports import router as reports_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database and ingest knowledge base
    print("Initializing Database...")
    init_db()
    print("Ingesting Knowledge Base Corpora into Vector Store...")
    rag_engine.ingest_knowledge_base()
    yield
    print("Application shutdown complete.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Intelligent Role-Based Candidate Screening System with Grounded RAG Architecture",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(interview_router, prefix=settings.API_PREFIX)
app.include_router(reports_router, prefix=settings.API_PREFIX)

# Static Frontend Files
STATIC_DIR = PROJECT_ROOT / "frontend" / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
async def root():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "PG-AGI Candidate Screening System Backend is running. Open /docs for Swagger API."}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "pgagi-candidate-screening",
        "knowledge_chunks": len(rag_engine.chunks),
        "db_initialized": settings.DB_PATH.exists()
    }
