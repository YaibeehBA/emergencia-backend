from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator

from app.schemas.base import BaseSchema, IDSchema


class EmergencyAdmissionRequest(BaseModel):
    """Request para webhook de admisión a emergencia"""

    cedula: str = Field(
        ...,
        min_length=10,
        max_length=10,
        description="Cédula del paciente (10 dígitos)",
        example="1234567890",
    )
    hospital_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="ID del hospital",
        example="HOSP-001",
    )
    hospital_name: Optional[str] = Field(
        None,
        description="Nombre del hospital",
        example="Hospital San Juan",
    )
    hospital_email: str = Field(
        ...,
        description="Email del departamento de admisiones",
        example="admisiones@hospital.com",
    )
    insurance_manager_email: str = Field(
        ...,
        description="Email del gestor de casos del seguro",
        example="casos@seguros.com",
    )
    admission_timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp de ingreso a emergencia",
    )

    @field_validator("cedula")
    @classmethod
    def cedula_must_be_digits(cls, v: str) -> str:
        """Validar que cédula sea solo dígitos"""
        if not v.isdigit():
            raise ValueError("Cédula debe contener solo dígitos")
        return v


class AgentDecisionResponse(BaseModel):
    """Respuesta de decisión del agente"""

    status: str = Field(
        ...,
        description="Estado de la decisión",
        example="APPROVED",
    )
    cedula: str = Field(..., description="Cédula del paciente")
    policy_number: Optional[str] = Field(None, description="Número de póliza")
    decision_reason: str = Field(
        ...,
        description="Razón de la decisión",
        example="Póliza activa, sin suspensiones, pre-existencias cubiertas",
    )
    confidence: float = Field(
        ...,
        ge=0,
        le=1,
        description="Confianza de la decisión (0-1)",
        example=0.95,
    )
    pre_existing_conditions: List[str] = Field(
        default_factory=list,
        description="Lista de pre-existencias del paciente",
    )
    is_suspended: bool = Field(
        ...,
        description="¿La póliza está suspendida?",
        example=False,
    )
    requires_manual_review: bool = Field(
        default=False,
        description="¿Requiere revisión manual?",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp de la decisión",
    )


class CaseResponse(IDSchema):
    """Respuesta de caso procesado"""

    cedula: str
    hospital_id: Optional[str]
    hospital_name: Optional[str]
    hospital_email: str
    agent_decision: dict
    notification_status: str
    hospital_notified_at: Optional[datetime] = None
    insurance_notified_at: Optional[datetime] = None
    processing_time_ms: Optional[int] = None
    admission_timestamp: datetime


class CaseListResponse(BaseSchema):
    """Respuesta de lista de casos"""

    total: int = Field(..., description="Total de casos")
    limit: int = Field(..., description="Límite de resultados")
    offset: int = Field(..., description="Offset de paginación")
    cases: List[CaseResponse] = Field(..., description="Lista de casos")
