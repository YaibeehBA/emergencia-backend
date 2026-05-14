"""
Base repository genérica para operaciones CRUD comunes.
Patrón Repository para abstraer lógica de acceso a datos.
"""

from typing import Generic, TypeVar, List, Optional, Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from app.db.base import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    """
    Repositorio base genérico para operaciones CRUD.
    Se usa para evitar duplicar código en cada repositorio.
    """

    def __init__(self, db: Session, model: type[T]):
        """
        Inicializa el repositorio.

        Args:
            db: SQLAlchemy session
            model: Modelo ORM
        """
        self.db = db
        self.model = model

    def create(self, **kwargs) -> T:
        """
        Crea una nueva instancia.

        Args:
            **kwargs: Campos del modelo

        Returns:
            Instancia creada
        """
        instance = self.model(**kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def get_by_id(self, id: int) -> Optional[T]:
        """Obtiene por ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """
        Obtiene todos los registros con paginación.

        Args:
            skip: Registros a saltar
            limit: Límite de registros

        Returns:
            Lista de registros
        """
        return (
            self.db.query(self.model)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count(self) -> int:
        """Cuenta total de registros"""
        return self.db.query(self.model).count()

    def update(self, id: int, **kwargs) -> Optional[T]:
        """
        Actualiza un registro.

        Args:
            id: ID del registro
            **kwargs: Campos a actualizar

        Returns:
            Instancia actualizada
        """
        instance = self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            self.db.commit()
            self.db.refresh(instance)
        return instance

    def delete(self, id: int) -> bool:
        """
        Elimina un registro.

        Args:
            id: ID del registro

        Returns:
            True si se eliminó, False si no existe
        """
        instance = self.get_by_id(id)
        if instance:
            self.db.delete(instance)
            self.db.commit()
            return True
        return False

    def exists(self, **kwargs) -> bool:
        """
        Verifica si existe un registro con los filtros.

        Args:
            **kwargs: Filtros

        Returns:
            True si existe
        """
        query = self.db.query(self.model)
        for key, value in kwargs.items():
            query = query.filter(getattr(self.model, key) == value)
        return query.first() is not None

    def filter(self, **kwargs) -> List[T]:
        """
        Filtra registros.

        Args:
            **kwargs: Filtros (AND)

        Returns:
            Lista de registros filtrados
        """
        query = self.db.query(self.model)
        for key, value in kwargs.items():
            query = query.filter(getattr(self.model, key) == value)
        return query.all()

    def get_or_create(self, defaults: Dict[str, Any] = None, **kwargs) -> tuple[T, bool]:
        """
        Obtiene o crea un registro.

        Args:
            defaults: Campos adicionales si se crea
            **kwargs: Filtros

        Returns:
            (instancia, created: bool)
        """
        instance = self.db.query(self.model).filter_by(**kwargs).first()

        if instance:
            return instance, False

        if defaults is None:
            defaults = {}

        instance = self.model(**{**kwargs, **defaults})
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)

        return instance, True
