from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session

from app.agents.emergency_agent import EmergencyAgent
from app.repositories.patient_repository import PatientRepository
from app.repositories.policy_repository import PolicyRepository
from app.repositories.case_repository import CaseRepository
from app.repositories.base_repository import BaseRepository
from app.db.models import Case, AuditLog
from app.schemas.emergency import EmergencyAdmissionRequest, AgentDecisionResponse
from app.services.notification_service import NotificationService
from app.utils.logger import get_logger
from app.utils.validators import validate_cedula
from app.utils.exceptions import PatientNotFoundError

logger = get_logger("services.emergency")


class EmergencyService:
    """Servicio para procesamiento de emergencias"""

    def __init__(self, db: Session):
        """
        Inicializa servicio.

        Args:
            db: SQLAlchemy session
        """
        self.db = db
        self.patient_repo = PatientRepository(db)
        self.policy_repo = PolicyRepository(db)
        self.case_repo = CaseRepository(db)
        self.audit_repo = BaseRepository(db, AuditLog)
        self.agent = EmergencyAgent(db)
        self.notification_service = NotificationService()

    def process_emergency_admission(
        self,
        request: EmergencyAdmissionRequest,
    ) -> Dict[str, Any]:
        """
        Procesa un ingreso a emergencia.

        Args:
            request: Datos del ingreso

        Returns:
            Caso procesado con decisión
        """
        logger.info(f"Procesando emergencia para cédula: {request.cedula}")

        # 1. Validar entrada
        if not validate_cedula(request.cedula):
            logger.error(f"Cédula inválida: {request.cedula}")
            raise ValueError(f"Cédula inválida: {request.cedula}")

        # 2. Obtener paciente (para audit trail)
        patient = self.patient_repo.get_by_cedula(request.cedula)
        patient_id = patient.id if patient else None

        # 3. Ejecutar agente
        logger.info("Ejecutando agente de validación...")
        agent_decision = self.agent.process_emergency(request.cedula)

        # 4. Crear registro de caso
        logger.info("Creando registro de caso...")
        case = self.case_repo.create(
            patient_id=patient_id,
            cedula=request.cedula,
            hospital_id=request.hospital_id,
            hospital_name=request.hospital_name,
            hospital_email=request.hospital_email,
            agent_decision=agent_decision,
            admission_timestamp=request.admission_timestamp,
            processing_time_ms=agent_decision.get("processing_time_ms"),
            notification_status="PENDING",
        )

        # 5. Crear audit log
        logger.info("Registrando en audit trail...")
        self.audit_repo.create(
            patient_id=patient_id,
            action="EMERGENCY_PROCESSED",
            details={
                "cedula": request.cedula,
                "hospital_id": request.hospital_id,
                "case_id": case.id,
            },
            agent_reasoning=agent_decision.get("decision_reason"),
            confidence_score=agent_decision.get("confidence"),
        )

        # 6. Enviar notificaciones (async en background)
        logger.info("Enviando notificaciones...")
        try:
            import asyncio
            # Ejecutar en background (no bloquear la respuesta)
            asyncio.create_task(
                self.notification_service.send_notification_async(
                    hospital_email=request.hospital_email,
                    insurance_email=request.insurance_manager_email,
                    hospital_name=request.hospital_name,
                    cedula=request.cedula,
                    decision=agent_decision,
                )
            )
            logger.info("Notificaciones en cola")
        except Exception as e:
            logger.error(f"Error enviando notificaciones: {str(e)}")

        logger.info(f"Emergencia procesada. Caso ID: {case.id}")

        return {
            "case_id": case.id,
            "cedula": request.cedula,
            "hospital_id": request.hospital_id,
            "hospital_email": request.hospital_email,
            "decision": agent_decision,
            "created_at": case.created_at.isoformat(),
        }

    def get_case_details(self, case_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene detalles de un caso.

        Args:
            case_id: ID del caso

        Returns:
            Detalles del caso o None
        """
        case = self.case_repo.get_by_id(case_id)

        if not case:
            logger.warning(f"Caso no encontrado: {case_id}")
            return None

        return {
            "id": case.id,
            "cedula": case.cedula,
            "hospital_id": case.hospital_id,
            "hospital_name": case.hospital_name,
            "agent_decision": case.agent_decision,
            "hospital_notified_at": case.hospital_notified_at.isoformat()
            if case.hospital_notified_at
            else None,
            "insurance_notified_at": case.insurance_notified_at.isoformat()
            if case.insurance_notified_at
            else None,
            "notification_status": case.notification_status,
            "processing_time_ms": case.processing_time_ms,
            "admission_timestamp": case.admission_timestamp.isoformat(),
            "created_at": case.created_at.isoformat(),
        }

    def get_recent_cases(
        self,
        limit: int = 20,
        hours: int = 24,
    ) -> Dict[str, Any]:
        """
        Obtiene casos recientes.

        Args:
            limit: Límite de resultados
            hours: Últimas N horas

        Returns:
            Lista de casos
        """
        cases = self.case_repo.get_recent_cases(limit=limit, hours=hours)

        return {
            "total": len(cases),
            "limit": limit,
            "hours": hours,
            "cases": [
                {
                    "id": case.id,
                    "cedula": case.cedula,
                    "hospital_name": case.hospital_name,
                    "status": case.agent_decision.get("status"),
                    "confidence": case.agent_decision.get("confidence"),
                    "decision_reason": case.agent_decision.get("decision_reason"),
                    "processing_time_ms": case.processing_time_ms,
                    "created_at": case.created_at.isoformat(),
                }
                for case in cases
            ],
        }

    def get_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Obtiene estadísticas de casos.

        Args:
            hours: Período de análisis

        Returns:
            Estadísticas
        """
        stats = self.case_repo.get_statistics(hours=hours)

        return {
            "period_hours": hours,
            "total_cases": stats["total_cases"],
            "approved": stats["approved"],
            "denied": stats["denied"],
            "pending": stats["pending"],
            "avg_processing_time_ms": round(stats["avg_processing_time_ms"], 2),
            "approval_rate": round(stats["approval_rate"] * 100, 2),
            "timestamp": datetime.utcnow().isoformat(),
        }