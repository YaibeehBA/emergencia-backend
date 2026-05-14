from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from app.db.models import AuditLog
from app.repositories.base_repository import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    """Repositorio para modelo AuditLog"""

    def __init__(self, db: Session):
        super().__init__(db, AuditLog)

    def get_by_patient(self, patient_id: int, limit: int = 50) -> List[AuditLog]:
        """
        Obtiene logs de auditoría de un paciente.

        Args:
            patient_id: ID del paciente
            limit: Límite de resultados

        Returns:
            Lista de logs
        """
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.patient_id == patient_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_by_action(self, action: str, limit: int = 100) -> List[AuditLog]:
        """
        Obtiene logs por tipo de acción.

        Args:
            action: Tipo de acción
            limit: Límite de resultados

        Returns:
            Lista de logs
        """
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.action == action)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_recent(self, hours: int = 24, limit: int = 100) -> List[AuditLog]:
        """
        Obtiene logs recientes.

        Args:
            hours: Últimas N horas
            limit: Límite de resultados

        Returns:
            Lista de logs
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        return (
            self.db.query(AuditLog)
            .filter(AuditLog.created_at >= cutoff_time)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_by_action_and_patient(
        self,
        action: str,
        patient_id: int,
    ) -> List[AuditLog]:
        """
        Obtiene logs de un paciente para una acción específica.

        Args:
            action: Tipo de acción
            patient_id: ID del paciente

        Returns:
            Lista de logs
        """
        return (
            self.db.query(AuditLog)
            .filter(
                AuditLog.action == action,
                AuditLog.patient_id == patient_id,
            )
            .order_by(AuditLog.created_at.desc())
            .all()
        )
