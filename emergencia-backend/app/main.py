import logging

logging.getLogger("watchfiles").setLevel(logging.ERROR)
logging.getLogger("watchfiles.main").setLevel(logging.ERROR)
logging.getLogger("watchfiles.run").setLevel(logging.ERROR)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db import init_db
from app.api import api_router
from app.utils.logger import setup_logging, get_logger

settings = get_settings()

setup_logging(
    log_level=settings.log_level,
    log_file=settings.log_file,
)

if settings.debug:
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    logging.info("Modo DEBUG activado - Logs SQL habilitados")

app_logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app_logger.info("Iniciando aplicación...")
    
    # Crear tablas
    init_db()
    app_logger.info("Base de datos inicializada")
    
    # Poblar datos de prueba
    try:
        from data.seed import populate_database
        populate_database()
        app_logger.info("Datos de prueba cargados")
    except Exception as e:
        app_logger.warning(f"No se pudieron cargar datos: {str(e)}")
    
    yield
    app_logger.info("Apagando aplicación...")


app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
async def root():
    return {"status": "ok", "service": settings.api_title}


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=8000,
        reload=settings.debug,
        reload_excludes=["logs/*", "*.log", "*.db", "logs/"],
    )