"""Schemas module - validación Pydantic"""

from app.schemas.base import BaseSchema, IDSchema, SuccessResponse, ErrorResponse
from app.schemas.emergency import EmergencyAdmissionRequest, AgentDecisionResponse, CaseResponse

__all__ = [
    "BaseSchema",
    "IDSchema",
    "SuccessResponse",
    "ErrorResponse",
    "EmergencyAdmissionRequest",
    "AgentDecisionResponse",
    "CaseResponse",
]
