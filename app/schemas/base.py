from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class BaseSchema(BaseModel):
    """Schema base con configuración común"""

    model_config = ConfigDict(
        from_attributes=True,  # Permite crear desde ORM models
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "created_at": "2024-01-01T12:00:00Z",
                    "updated_at": "2024-01-01T12:00:00Z",
                }
            ]
        },
    )


class TimestampSchema(BaseSchema):
    """Schema con timestamps"""

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class IDSchema(TimestampSchema):
    """Schema con ID y timestamps"""

    id: Optional[int] = None


class SuccessResponse(BaseModel):
    """Respuesta estándar de éxito"""

    model_config = ConfigDict(json_schema_extra={"example": {"success": True, "message": "Operación completada"}})

    success: bool = True
    message: str = "Operación completada exitosamente"
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Respuesta estándar de error"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "error": "ERROR_CODE",
                "message": "Descripción del error",
                "details": None,
            }
        }
    )

    success: bool = False
    error: str = "ERROR"
    message: str = "Ocurrió un error"
    details: Optional[dict] = None
