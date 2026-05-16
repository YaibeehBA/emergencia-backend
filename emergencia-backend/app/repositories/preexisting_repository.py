"""
Repositorio para pre-existencias.
"""

from typing import List

from sqlalchemy.orm import Session

from app.db.models import PreExistingCondition
from app.repositories.base_repository import BaseRepository


class PreExistingRepository(BaseRepository[PreExistingCondition]):
    """Repositorio para modelo PreExistingCondition"""

    def __init__(self, db: Session):
        super().__init__(db, PreExistingCondition)

    def get_by_patient(self, patient_id: int) -> List[PreExistingCondition]:
        """
        Obtiene todas las pre-existencias de un paciente.

        Args:
            patient_id: ID del paciente

        Returns:
            Lista de pre-existencias
        """
        return (
            self.db.query(PreExistingCondition)
            .filter(PreExistingCondition.patient_id == patient_id)
            .all()
        )

    def get_uncovered(self, patient_id: int) -> List[PreExistingCondition]:
        """
        Obtiene pre-existencias NO cubiertas en emergencia.

        Args:
            patient_id: ID del paciente

        Returns:
            Lista de pre-existencias no cubiertas
        """
        return (
            self.db.query(PreExistingCondition)
            .filter(
                PreExistingCondition.patient_id == patient_id,
                PreExistingCondition.covered_in_emergency == False,
            )
            .all()
        )

    def has_uncovered_conditions(self, patient_id: int) -> bool:
        """
        Verifica si paciente tiene pre-existencias no cubiertas.

        Args:
            patient_id: ID del paciente

        Returns:
            True si hay pre-existencias no cubiertas
        """
        return len(self.get_uncovered(patient_id)) > 0
