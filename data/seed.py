import json
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy.orm import Session

from app.db import SessionLocal, init_db
from app.db.models import Patient, Policy, PreExistingCondition, Suspension, AuditLog
from app.core.constants import PolicyStatus, DecisionStatus


def seed_database():
    """Carga datos de prueba en la base de datos"""

    # Inicializar BD
    init_db()

    db = SessionLocal()

    try:
        # Verificar si ya hay datos
        if db.query(Patient).count() > 0:
            print("La base de datos ya contiene datos. Saltando seed...")
            return

        # ====================================================================
        # PACIENTES
        # ====================================================================
        patients = [
            Patient(
                cedula="1234567890",
                full_name="Juan Pérez García",
                date_of_birth=datetime(1980, 5, 15),
                email="juan.perez@email.com",
                phone="+593987654321",
                gender="M",
                emergency_contact_name="María Pérez",
                emergency_contact_phone="+593987654322",
            ),
            Patient(
                cedula="1234567891",
                full_name="María García López",
                date_of_birth=datetime(1985, 10, 22),
                email="maria.garcia@email.com",
                phone="+593987654323",
                gender="F",
                emergency_contact_name="Carlos García",
                emergency_contact_phone="+593987654324",
            ),
            Patient(
                cedula="1234567892",
                full_name="Carlos López Martínez",
                date_of_birth=datetime(1978, 3, 8),
                email="carlos.lopez@email.com",
                phone="+593987654325",
                gender="M",
                emergency_contact_name="Ana López",
                emergency_contact_phone="+593987654326",
            ),
            Patient(
                cedula="1234567893",
                full_name="Ana Martínez Rodríguez",
                date_of_birth=datetime(1992, 7, 12),
                email="ana.martinez@email.com",
                phone="+593987654327",
                gender="F",
                emergency_contact_name="Luis Martínez",
                emergency_contact_phone="+593987654328",
            ),
            Patient(
                cedula="1234567894",
                full_name="Luis Rodríguez Díaz",
                date_of_birth=datetime(1988, 1, 25),
                email="luis.rodriguez@email.com",
                phone="+593987654329",
                gender="M",
                emergency_contact_name="Rosa Rodríguez",
                emergency_contact_phone="+593987654330",
            ),
        ]

        db.add_all(patients)
        db.commit()

        print(f"{len(patients)} pacientes creados")

        # ====================================================================
        # PÓLIZAS
        # ====================================================================
        policies = [
            Policy(
                policy_number="POL-001001",
                patient_id=patients[0].id,
                status=PolicyStatus.ACTIVE,
                effective_date=datetime.utcnow() - timedelta(days=365),
                expiry_date=datetime.utcnow() + timedelta(days=365),
                plan_type="PREMIUM",
                coverage_percentage=100,
                copay_percentage=10,
                max_copay_monthly=100.00,
                insurance_company_name="Seguros Ecuador S.A.",
                insurance_manager_email="casos@segurosecuador.com",
            ),
            Policy(
                policy_number="POL-001002",
                patient_id=patients[1].id,
                status=PolicyStatus.ACTIVE,
                effective_date=datetime.utcnow() - timedelta(days=180),
                expiry_date=datetime.utcnow() + timedelta(days=180),
                plan_type="STANDARD",
                coverage_percentage=80,
                copay_percentage=15,
                max_copay_monthly=80.00,
                insurance_company_name="Seguros América",
                insurance_manager_email="casos@segurosamerica.com",
            ),
            Policy(
                policy_number="POL-001003",
                patient_id=patients[2].id,
                status=PolicyStatus.SUSPENDED,
                effective_date=datetime.utcnow() - timedelta(days=365),
                expiry_date=datetime.utcnow() + timedelta(days=365),
                plan_type="PREMIUM",
                coverage_percentage=100,
                copay_percentage=10,
                max_copay_monthly=100.00,
                insurance_company_name="Seguros Ecuador S.A.",
                insurance_manager_email="casos@segurosecuador.com",
            ),
            Policy(
                policy_number="POL-001004",
                patient_id=patients[3].id,
                status=PolicyStatus.ACTIVE,
                effective_date=datetime.utcnow() - timedelta(days=90),
                expiry_date=datetime.utcnow() + timedelta(days=275),
                plan_type="BASIC",
                coverage_percentage=60,
                copay_percentage=20,
                max_copay_monthly=60.00,
                insurance_company_name="Seguros Vida",
                insurance_manager_email="casos@segurosVida.com",
            ),
            Policy(
                policy_number="POL-001005",
                patient_id=patients[4].id,
                status=PolicyStatus.EXPIRED,
                effective_date=datetime.utcnow() - timedelta(days=730),
                expiry_date=datetime.utcnow() - timedelta(days=30),
                plan_type="STANDARD",
                coverage_percentage=80,
                copay_percentage=15,
                max_copay_monthly=80.00,
                insurance_company_name="Seguros América",
                insurance_manager_email="casos@segurosamerica.com",
            ),
        ]

        db.add_all(policies)
        db.commit()

        print(f"{len(policies)} pólizas creadas")

        # ====================================================================
        # PRE-EXISTENCIAS
        # ====================================================================
        preexisting = [
            PreExistingCondition(
                patient_id=patients[0].id,
                condition_name="Diabetes Tipo 2",
                diagnosis_date=datetime(2015, 6, 1),
                description="Controlada con medicamentos",
                covered_in_emergency=True,
                coverage_percentage=100,
            ),
            PreExistingCondition(
                patient_id=patients[0].id,
                condition_name="Hipertensión",
                diagnosis_date=datetime(2018, 3, 15),
                description="Presión arterial controlada",
                covered_in_emergency=True,
                coverage_percentage=100,
            ),
            PreExistingCondition(
                patient_id=patients[1].id,
                condition_name="Asma",
                diagnosis_date=datetime(2012, 9, 20),
                description="Asma moderada",
                covered_in_emergency=True,
                coverage_percentage=100,
            ),
            PreExistingCondition(
                patient_id=patients[2].id,
                condition_name="Artritis Reumatoide",
                diagnosis_date=datetime(2010, 1, 10),
                description="Progresiva",
                covered_in_emergency=False,
                coverage_percentage=50,
                exclusion_reason="Condición preexistente con restricción",
            ),
            PreExistingCondition(
                patient_id=patients[3].id,
                condition_name="Tiroidismo",
                diagnosis_date=datetime(2016, 5, 22),
                description="Hipotiroidismo compensado",
                covered_in_emergency=True,
                coverage_percentage=100,
            ),
        ]

        db.add_all(preexisting)
        db.commit()

        print(f"{len(preexisting)} pre-existencias creadas")

        # ====================================================================
        # SUSPENSIONES
        # ====================================================================
        suspensions = [
            Suspension(
                policy_id=policies[2].id,  # POL-001003
                reason="Falta de pago",
                suspended_date=datetime.utcnow() - timedelta(days=30),
                until_date=datetime.utcnow() + timedelta(days=30),
                is_active=True,
                notes="Pago pendiente de 3 meses",
            ),
        ]

        db.add_all(suspensions)
        db.commit()

        print(f"{len(suspensions)} suspensiones creadas")

        # ====================================================================
        # AUDIT LOGS (iniciales)
        # ====================================================================
        audit_logs = [
            AuditLog(
                patient_id=patients[0].id,
                action="PATIENT_CREATED",
                details={"method": "seed_script"},
            ),
            AuditLog(
                patient_id=patients[1].id,
                action="PATIENT_CREATED",
                details={"method": "seed_script"},
            ),
        ]

        db.add_all(audit_logs)
        db.commit()

        print(f"{len(audit_logs)} audit logs creados")

        # ====================================================================
        # RESUMEN
        # ====================================================================
        print("\n" + "=" * 60)
        print("BASE DE DATOS POBLADA EXITOSAMENTE")
        print("=" * 60)
        print(f"Total de registros:")
        print(f"   - Pacientes: {db.query(Patient).count()}")
        print(f"   - Pólizas: {db.query(Policy).count()}")
        print(f"   - Pre-existencias: {db.query(PreExistingCondition).count()}")
        print(f"   - Suspensiones: {db.query(Suspension).count()}")
        print(f"   - Audit Logs: {db.query(AuditLog).count()}")
        print("=" * 60)

        print("\nCédulas de prueba disponibles:")
        for patient in patients:
            print(f"   - {patient.cedula}: {patient.full_name}")

    except Exception as e:
        db.rollback()
        print(f"Error al poblar BD: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import os
    import sys

    # Añadir directorio padre al path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    seed_database()
