"""
Tools para el agente IA.
Funciones que el agente puede llamar para obtener datos.
"""
import json
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.db.models import Patient, Policy, PreExistingCondition, Suspension
from app.core.constants import PolicyStatus
from app.utils.logger import get_logger
from app.utils.exceptions import PatientNotFoundError, PolicyNotFoundError

logger = get_logger("agents.tools")


class AgentTools:
    """Contenedor para tools del agente"""

    def __init__(self, db: Session):
        """
        Inicializa tools con sesión de BD.

        Args:
            db: SQLAlchemy session
        """
        self.db = db

    def check_policy(self, cedula: str) -> Dict[str, Any]:
        """
        Verifica póliza activa de un paciente.

        Args:
            cedula: Cédula del paciente

        Returns:
            Dict con información de póliza
        """
        try:
            logger.info(f"Buscando póliza para cédula: {cedula}")

            # Obtener paciente
            patient = (
                self.db.query(Patient).filter(Patient.cedula == cedula).first()
            )

            if not patient:
                logger.warning(f"Paciente no encontrado: {cedula}")
                return {
                    "success": False,
                    "error": "PATIENT_NOT_FOUND",
                    "message": f"Paciente con cédula {cedula} no existe en el sistema",
                    "cedula": cedula,
                }

            # Obtener póliza activa
            policy = (
                self.db.query(Policy)
                .filter(
                    Policy.patient_id == patient.id,
                    Policy.status == PolicyStatus.ACTIVE,
                )
                .first()
            )

            if not policy:
                logger.warning(f"No hay póliza activa para: {cedula}")
                return {
                    "success": False,
                    "error": "NO_ACTIVE_POLICY",
                    "message": f"Paciente sin póliza activa",
                    "cedula": cedula,
                    "patient_id": patient.id,
                }

            # Validar fechas
            now = datetime.utcnow()
            is_valid = policy.effective_date <= now <= policy.expiry_date

            logger.info(
                f"Póliza encontrada: {policy.policy_number} (válida: {is_valid})"
            )

            return {
                "success": True,
                "cedula": cedula,
                "patient_id": patient.id,
                "patient_name": patient.full_name,
                "policy_number": policy.policy_number,
                "status": policy.status,
                "effective_date": policy.effective_date.isoformat(),
                "expiry_date": policy.expiry_date.isoformat(),
                "is_valid_dates": is_valid,
                "plan_type": policy.plan_type,
                "coverage_percentage": policy.coverage_percentage,
                "copay_percentage": policy.copay_percentage,
                "insurance_company": policy.insurance_company_name,
            }

        except Exception as e:
            logger.error(f"Error verificando póliza: {str(e)}", exc_info=e)
            return {
                "success": False,
                "error": "CHECK_POLICY_ERROR",
                "message": f"Error: {str(e)}",
            }

    def check_preexisting(self, patient_id: int, cedula: str) -> Dict[str, Any]:
        """
        Verifica pre-existencias del paciente.

        Args:
            patient_id: ID del paciente
            cedula: Cédula para logging

        Returns:
            Dict con pre-existencias
        """
        try:
            logger.info(f"Buscando pre-existencias para paciente: {patient_id}")

            preexisting = (
                self.db.query(PreExistingCondition)
                .filter(PreExistingCondition.patient_id == patient_id)
                .all()
            )

            if not preexisting:
                logger.info(f"Paciente sin pre-existencias registradas")
                return {
                    "success": True,
                    "patient_id": patient_id,
                    "has_preexisting": False,
                    "conditions": [],
                    "all_covered_in_emergency": True,
                }

            # Convertir a lista de dicts
            conditions_list = []
            uncovered_count = 0

            for condition in preexisting:
                conditions_list.append({
                    "condition_name": condition.condition_name,
                    "diagnosis_date": condition.diagnosis_date.isoformat()
                    if condition.diagnosis_date
                    else None,
                    "covered_in_emergency": condition.covered_in_emergency,
                    "coverage_percentage": condition.coverage_percentage,
                    "exclusion_reason": condition.exclusion_reason,
                })

                if not condition.covered_in_emergency:
                    uncovered_count += 1

            logger.info(
                f"{len(preexisting)} pre-existencias encontradas ({uncovered_count} no cubiertas)"
            )

            return {
                "success": True,
                "patient_id": patient_id,
                "has_preexisting": True,
                "conditions_count": len(preexisting),
                "conditions": conditions_list,
                "all_covered_in_emergency": uncovered_count == 0,
                "uncovered_count": uncovered_count,
            }

        except Exception as e:
            logger.error(f"Error verificando pre-existencias: {str(e)}", exc_info=e)
            return {
                "success": False,
                "error": "CHECK_PREEXISTING_ERROR",
                "message": f"Error: {str(e)}",
            }

    def check_suspension(self, policy_id: int, cedula: str) -> Dict[str, Any]:
        """
        Verifica si póliza está suspendida.

        Args:
            policy_id: ID de la póliza
            cedula: Cédula para logging

        Returns:
            Dict con estado de suspensión
        """
        try:
            logger.info(f"Verificando suspensiones para póliza: {policy_id}")

            suspension = (
                self.db.query(Suspension)
                .filter(
                    Suspension.policy_id == policy_id,
                    Suspension.is_active == True,
                )
                .first()
            )

            if not suspension:
                logger.info(f"Póliza sin suspensiones activas")
                return {
                    "success": True,
                    "policy_id": policy_id,
                    "is_suspended": False,
                    "suspension_reason": None,
                    "suspended_date": None,
                    "until_date": None,
                }

            logger.warning(
                f"Póliza suspendida: {suspension.reason}"
            )

            return {
                "success": True,
                "policy_id": policy_id,
                "is_suspended": True,
                "suspension_reason": suspension.reason,
                "suspended_date": suspension.suspended_date.isoformat(),
                "until_date": suspension.until_date.isoformat()
                if suspension.until_date
                else None,
                "notes": suspension.notes,
            }

        except Exception as e:
            logger.error(f"Error verificando suspensión: {str(e)}", exc_info=e)
            return {
                "success": False,
                "error": "CHECK_SUSPENSION_ERROR",
                "message": f"Error: {str(e)}",
            }

    def get_all_tools_as_dict(self) -> Dict[str, Any]:
        """
        Retorna descripción de tools para LangChain.

        Returns:
            Dict con definición de tools
        """
        return {
            "check_policy": {
                "description": "Verifica póliza activa del paciente por cédula",
                "parameters": {
                    "cedula": "Número de cédula del paciente (10 dígitos)"
                },
            },
            "check_preexisting": {
                "description": "Obtiene pre-existencias del paciente",
                "parameters": {
                    "patient_id": "ID del paciente",
                    "cedula": "Cédula para logging",
                },
            },
            "check_suspension": {
                "description": "Verifica si póliza tiene suspensiones activas",
                "parameters": {
                    "policy_id": "ID de la póliza",
                    "cedula": "Cédula para logging",
                },
            },
        }
