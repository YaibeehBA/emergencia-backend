"""
Repositorio para operaciones con pacientes.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import Patient
from app.repositories.base_repository import BaseRepository


class PatientRepository(BaseRepository[Patient]):
    """Repositorio para modelo Patient"""

    def __init__(self, db: Session):
        super().__init__(db, Patient)

    def get_by_cedula(self, cedula: str) -> Optional[Patient]:
        """
        Obtiene paciente por cédula.

        Args:
            cedula: Número de cédula

        Returns:
            Patient o None
        """
        return self.db.query(Patient).filter(Patient.cedula == cedula).first()

    def get_by_email(self, email: str) -> Optional[Patient]:
        """Obtiene paciente por email"""
        return self.db.query(Patient).filter(Patient.email == email).first()

    def get_with_policies(self, cedula: str) -> Optional[Patient]:
        """
        Obtiene paciente con todas sus pólizas.

        Args:
            cedula: Número de cédula

        Returns:
            Patient con relaciones cargadas
        """
        return (
            self.db.query(Patient)
            .filter(Patient.cedula == cedula)
            .first()
        )
