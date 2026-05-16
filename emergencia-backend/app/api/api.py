from fastapi import APIRouter
from app.api.routes import emergency, health

# Crear router principal
api_router = APIRouter()

# Incluir rutas
api_router.include_router(health.router)
api_router.include_router(emergency.router)
