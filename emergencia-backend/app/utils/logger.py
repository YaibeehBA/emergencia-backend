import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Formateador JSON personalizado para logs"""

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        super().add_fields(log_record, record, message_dict)
        log_record["timestamp"] = datetime.utcnow().isoformat()
        log_record["level"] = record.levelname
        log_record["logger"] = record.name


def setup_logging(log_level: str = "INFO", log_file: str = None) -> logging.Logger:
    """
    Configura logging estructurado.
    """
    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Limpiar handlers existentes
    root_logger.handlers.clear()
    
    # Handler para archivo (con formato JSON)
    if log_file:
        log_path = Path(log_file).parent
        log_path.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(CustomJsonFormatter())
        root_logger.addHandler(file_handler)
    
    # Configurar loggers específicos
    # SQLAlchemy
    sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
    sqlalchemy_logger.setLevel(logging.INFO)
    sqlalchemy_logger.propagate = True  # Importante: permite que los logs lleguen al root
    
    # Asegurar que no haya handlers propios que interfieran
    sqlalchemy_logger.handlers.clear()
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene logger con nombre específico.
    """
    return logging.getLogger(f"emergencia-sync.{name}")