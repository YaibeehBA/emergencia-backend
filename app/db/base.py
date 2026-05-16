from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class BaseModel(Base):
  
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convierte el modelo a diccionario"""
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
        }

    def __repr__(self):
        """Representación en string"""
        return f"<{self.__class__.__name__}(id={self.id})>"
