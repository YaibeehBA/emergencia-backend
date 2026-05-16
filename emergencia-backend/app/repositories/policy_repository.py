"""
Repositorio para operaciones con pólizas.
"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session

from app.db.models import Policy
from app.repositories.base_repository import BaseRepository


class PolicyRepository(BaseRepository[Policy]):
    """Repositorio para modelo Policy"""

    def __init__(self, db: Session):
        super().__init__(db, Policy)

    def get_by_policy_number(self, policy_number: str) -> Optional[Policy]:
        """
        Obtiene póliza por número.

        Args:
            policy_number: Número de póliza

        Returns:
            Policy o None
        """
        return (
            self.db.query(Policy)
            .filter(Policy.policy_number == policy_number)
            .first()
        )

    def get_active_by_patient(self, patient_id: int) -> Optional[Policy]:
        """
        Obtiene póliza activa de un paciente.

        Args:
            patient_id: ID del paciente

        Returns:
            Policy activa o None
        """
        from app.core.constants import PolicyStatus

        return (
            self.db.query(Policy)
            .filter(
                Policy.patient_id == patient_id,
                Policy.status == PolicyStatus.ACTIVE,
                Policy.effective_date <= datetime.utcnow(),
                Policy.expiry_date >= datetime.utcnow(),
            )
            .first()
        )

    def get_all_by_patient(self, patient_id: int) -> List[Policy]:
        """
        Obtiene todas las pólizas de un paciente.

        Args:
            patient_id: ID del paciente

        Returns:
            Lista de pólizas
        """
        return (
            self.db.query(Policy)
            .filter(Policy.patient_id == patient_id)
            .all()
        )

    def is_expired(self, policy_id: int) -> bool:
        """
        Verifica si una póliza está expirada.

        Args:
            policy_id: ID de la póliza

        Returns:
            True si está expirada
        """
        policy = self.get_by_id(policy_id)
        if not policy:
            return True

        return policy.expiry_date < datetime.utcnow()

    def is_active_and_valid(self, policy_id: int) -> bool:
        """
        Verifica si una póliza está activa y válida.

        Args:
            policy_id: ID de la póliza

        Returns:
            True si está activa y válida
        """
        from app.core.constants import PolicyStatus

        policy = self.get_by_id(policy_id)
        if not policy:
            return False

        return (
            policy.status == PolicyStatus.ACTIVE
            and policy.effective_date <= datetime.utcnow()
            and policy.expiry_date >= datetime.utcnow()
        )
