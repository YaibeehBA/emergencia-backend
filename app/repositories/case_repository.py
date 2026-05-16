"""
Repositorio para casos de emergencia.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session

from app.db.models import Case
from app.repositories.base_repository import BaseRepository


class CaseRepository(BaseRepository[Case]):
    """Repositorio para modelo Case"""

    def __init__(self, db: Session):
        super().__init__(db, Case)

    def get_recent_cases(
        self,
        limit: int = 20,
        hours: int = 24,
    ) -> List[Case]:
        """
        Obtiene casos recientes.

        Args:
            limit: Límite de resultados
            hours: Últimas N horas

        Returns:
            Lista de casos
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        return (
            self.db.query(Case)
            .filter(Case.created_at >= cutoff_time)
            .order_by(Case.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_by_cedula(self, cedula: str) -> List[Case]:
        """
        Obtiene todos los casos de un paciente por cédula.

        Args:
            cedula: Cédula del paciente

        Returns:
            Lista de casos
        """
        return (
            self.db.query(Case)
            .filter(Case.cedula == cedula)
            .order_by(Case.created_at.desc())
            .all()
        )

    def get_by_patient_id(self, patient_id: int) -> List[Case]:
        """Obtiene todos los casos de un paciente"""
        return (
            self.db.query(Case)
            .filter(Case.patient_id == patient_id)
            .order_by(Case.created_at.desc())
            .all()
        )

    def get_by_hospital(self, hospital_id: str, limit: int = 50) -> List[Case]:
        """
        Obtiene casos de un hospital.

        Args:
            hospital_id: ID del hospital
            limit: Límite de resultados

        Returns:
            Lista de casos
        """
        return (
            self.db.query(Case)
            .filter(Case.hospital_id == hospital_id)
            .order_by(Case.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_pending_notifications(self) -> List[Case]:
        """
        Obtiene casos con notificaciones pendientes.

        Returns:
            Lista de casos
        """
        return (
            self.db.query(Case)
            .filter(Case.notification_status == "PENDING")
            .all()
        )

    def count_by_status(self, status: str) -> int:
        """
        Cuenta casos por estado de decisión.

        Args:
            status: Estado (APPROVED, DENIED, etc)

        Returns:
            Número de casos
        """
        return (
            self.db.query(Case)
            .filter(
                Case.agent_decision["status"].astext == status
            )
            .count()
        )

    def get_statistics(self, hours: int = 24) -> dict:
        """
        Obtiene estadísticas de casos recientes.

        Args:
            hours: Últimas N horas

        Returns:
            Diccionario con estadísticas
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        cases = (
            self.db.query(Case)
            .filter(Case.created_at >= cutoff_time)
            .all()
        )

        total = len(cases)
        approved = sum(
            1
            for case in cases
            if case.agent_decision.get("status") == "APPROVED"
        )
        denied = sum(
            1
            for case in cases
            if case.agent_decision.get("status") == "DENIED"
        )
        pending = sum(
            1
            for case in cases
            if case.agent_decision.get("status") == "PENDING_DOCUMENTS"
        )

        avg_processing_time = (
            sum(case.processing_time_ms for case in cases if case.processing_time_ms)
            / sum(1 for case in cases if case.processing_time_ms)
            if any(case.processing_time_ms for case in cases)
            else 0
        )

        return {
            "total_cases": total,
            "approved": approved,
            "denied": denied,
            "pending": pending,
            "avg_processing_time_ms": avg_processing_time,
            "approval_rate": approved / total if total > 0 else 0,
        }
