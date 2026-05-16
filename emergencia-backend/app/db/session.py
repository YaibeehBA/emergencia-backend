import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import get_settings

settings = get_settings()


if settings.debug:
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").propagate = True  # Permitir propagación
else:
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# Crear engine
engine = create_engine(
    settings.database_url,
    connect_args={
        "check_same_thread": False
    } if "sqlite" in settings.database_url else {},
    echo=False,  # IMPORTANTE: False para no usar print
    echo_pool=False,
    pool_pre_ping=True,
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app.db.base import Base
    Base.metadata.create_all(bind=engine)