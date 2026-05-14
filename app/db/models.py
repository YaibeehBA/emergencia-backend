from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
    Float,
    Text,
    ForeignKey,
    JSON,
    Index,
)
from sqlalchemy.orm import relationship
from app.db.base import BaseModel
from app.core.constants import PolicyStatus, DecisionStatus


class Patient(BaseModel):
    """Modelo de Paciente/Afiliado"""

    __tablename__ = "patients"

    # Información básica
    cedula = Column(String(20), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    date_of_birth = Column(DateTime, nullable=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    gender = Column(String(10), nullable=True)  # M, F, O

    # Información de contacto de emergencia
    emergency_contact_name = Column(String(255), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)

    # Relaciones
    policies = relationship("Policy", back_populates="patient", cascade="all, delete-orphan")
    preexisting_conditions = relationship(
        "PreExistingCondition",
        back_populates="patient",
        cascade="all, delete-orphan",
    )
    cases = relationship("Case", back_populates="patient", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Patient(cedula={self.cedula}, name={self.full_name})>"


class Policy(BaseModel):
    """Modelo de Póliza de Seguro"""

    __tablename__ = "policies"

    # Información de póliza
    policy_number = Column(String(50), unique=True, nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    status = Column(String(20), default=PolicyStatus.ACTIVE, nullable=False)
    # ACTIVE, SUSPENDED, EXPIRED, CANCELLED

    # Fechas
    effective_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=False)

    # Plan y cobertura
    plan_type = Column(String(50), nullable=False)  # PREMIUM, STANDARD, BASIC
    coverage_percentage = Column(Integer, default=100)
    copay_percentage = Column(Integer, default=10)
    max_copay_monthly = Column(Float, default=100.00)

    # Información del asegurador
    insurance_company_name = Column(String(255), nullable=False)
    insurance_manager_email = Column(String(255), nullable=False)

    # Relaciones
    patient = relationship("Patient", back_populates="policies")
    suspensions = relationship(
        "Suspension",
        back_populates="policy",
        cascade="all, delete-orphan",
    )

    # Índices para búsquedas rápidas
    __table_args__ = (
        Index("idx_policy_patient_status", "patient_id", "status"),
        Index("idx_policy_dates", "effective_date", "expiry_date"),
    )

    def __repr__(self):
        return f"<Policy(number={self.policy_number}, status={self.status})>"


class PreExistingCondition(BaseModel):
    """Modelo de Pre-existencias (condiciones previas)"""

    __tablename__ = "preexisting_conditions"

    # Información de condición
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    condition_name = Column(String(255), nullable=False)
    diagnosis_date = Column(DateTime, nullable=True)
    description = Column(Text, nullable=True)

    # Cobertura
    covered_in_emergency = Column(Boolean, default=True)
    coverage_percentage = Column(Integer, default=100)
    exclusion_reason = Column(String(255), nullable=True)

    # Relaciones
    patient = relationship("Patient", back_populates="preexisting_conditions")

    def __repr__(self):
        return f"<PreExistingCondition(patient_id={self.patient_id}, condition={self.condition_name})>"


class Suspension(BaseModel):
    """Modelo de Suspensión de Póliza"""

    __tablename__ = "suspensions"

    policy_id = Column(Integer, ForeignKey("policies.id"), nullable=False, index=True)
    reason = Column(String(255), nullable=False)
    suspended_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    until_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    notes = Column(Text, nullable=True)

    # Relaciones
    policy = relationship("Policy", back_populates="suspensions")

    def __repr__(self):
        return f"<Suspension(policy_id={self.policy_id}, reason={self.reason})>"


class Case(BaseModel):
    """Modelo de Caso de Emergencia Procesado"""

    __tablename__ = "cases"

    # Información del paciente
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    cedula = Column(String(20), nullable=False, index=True)

    # Hospital
    hospital_id = Column(String(50), nullable=True)
    hospital_name = Column(String(255), nullable=True)
    hospital_email = Column(String(255), nullable=False)

    # Decisión del agente
    agent_decision = Column(JSON, nullable=False)
    # {
    #   "status": "APPROVED",
    #   "decision_reason": "...",
    #   "confidence": 0.95,
    #   "pre_existing_conditions": ["..."],
    #   "is_suspended": false
    # }

    # Notificaciones
    hospital_notified_at = Column(DateTime, nullable=True)
    insurance_notified_at = Column(DateTime, nullable=True)
    notification_status = Column(String(50), default="PENDING")
    # PENDING, SENT, FAILED, RETRY

    # Metadata
    processing_time_ms = Column(Integer, nullable=True)
    admission_timestamp = Column(DateTime, nullable=False)

    # Relaciones
    patient = relationship("Patient", back_populates="cases")

    # Índices
    __table_args__ = (
        Index("idx_case_patient_timestamp", "patient_id", "created_at"),
        Index("idx_case_hospital_timestamp", "hospital_id", "created_at"),
    )

    def __repr__(self):
        return f"<Case(cedula={self.cedula}, status={self.agent_decision.get('status')})>"


class AuditLog(BaseModel):
    """Modelo de Audit Trail (Registro de Auditoría)"""

    __tablename__ = "audit_logs"

    # Quién y qué
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    # EMERGENCY_RECEIVED, AGENT_DECISION, NOTIFICATION_SENT, etc

    # Detalles
    details = Column(JSON, nullable=True)
    agent_reasoning = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)

    # Metadata
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)

    # Índices
    __table_args__ = (
        Index("idx_audit_patient_action", "patient_id", "action"),
        Index("idx_audit_timestamp", "created_at"),
    )

    def __repr__(self):
        return f"<AuditLog(action={self.action}, timestamp={self.created_at})>"
