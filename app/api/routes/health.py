from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db import get_db
from app.utils.logger import get_logger

logger = get_logger("api.routes.health")

router = APIRouter(
    tags=["Health"],
)

settings = get_settings()


@router.get(
    "/health",
    summary="Health check",
    description="Verifica estado de la aplicación",
)
async def health_check(db: Session = Depends(get_db)):
    """
    Health check básico.

    Verifica:
    - API respondiendo
    - BD conectada
    """
    try:
        # Verificar BD
        db.execute("SELECT 1")

        return {
            "status": "healthy",
            "version": settings.api_version,
            "environment": settings.environment,
            "database": "connected",
        }

    except Exception as e:
        logger.error(f"Health check fallido: {str(e)}")

        return {
            "status": "unhealthy",
            "version": settings.api_version,
            "environment": settings.environment,
            "database": "disconnected",
            "error": str(e),
        }


@router.get(
    "/",
    summary="Info de API",
    description="Información general de la API",
)
async def root():
    """Información de la API"""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "description": settings.api_description,
        "environment": settings.environment,
        "docs": "/docs",
        "health": "/health",
    }
