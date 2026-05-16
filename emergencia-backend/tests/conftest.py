
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db import session as db_session


# Engine de prueba (SQLite en memoria)
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture
def db():
    """
    Fixture que proporciona BD de prueba.
    Crea tablas antes y limpia después.
    """
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_patient_data():
    """Datos de prueba para paciente"""
    from datetime import datetime

    return {
        "cedula": "1234567890",
        "full_name": "Test Patient",
        "email": "test@email.com",
        "phone": "+593987654321",
        "gender": "M",
    }


@pytest.fixture
def test_policy_data():
    """Datos de prueba para póliza"""
    from datetime import datetime, timedelta

    return {
        "policy_number": "POL-TEST-001",
        "status": "ACTIVE",
        "effective_date": datetime.utcnow() - timedelta(days=365),
        "expiry_date": datetime.utcnow() + timedelta(days=365),
        "plan_type": "PREMIUM",
        "coverage_percentage": 100,
        "insurance_company_name": "Test Insurance",
        "insurance_manager_email": "test@insurance.com",
    }
