from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    """
    Configuración de la aplicación.
    Las variables se cargan desde .env automáticamente.
    """

    # API
    api_title: str = "Emergencia-Sync"
    api_version: str = "1.0.0"
    api_description: str = "Sistema de Alerta Temprana de Ingresos a Emergencias"
    environment: str = "development"
    debug: bool = False

    # DATABASE
    database_url: str = "sqlite:///./emergencia.db"

    # AI/AGENTS - MÚLTIPLES PROVEEDORES
    active_agent: str = "groq"  
    
    # Google Gemini
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-2.5-flash"
    
    # Groq
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.3-70b-versatile"
    
    # Configuración común
    agent_temperature: float = 0.7
    agent_max_tokens: int = 1000

    # EMAIL
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    sender_email: str = "noreply@emergencia-sync.com"
    sender_name: str = "Emergencia-Sync"
    mock_email: bool = False  

    # SECURITY
    secret_key: str = "tu-secret-key-cambia-en-produccion"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
   cors_origins: list = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost",
    "https://emergencia-fronted.up.railway.app",
]

    # LOGGING
    log_level: str = "INFO"
    log_file: Optional[str] = "logs/app.webhook"

    # WEBHOOK
    webhook_secret: str = "webhook-secret"
    webhook_timeout_seconds: int = 30

    # Configuración explícita de Pydantic
    model_config = ConfigDict(
        env_file=".env",          # Archivo .env en la raíz
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Retorna instancia cacheada de Settings."""
    return Settings()
