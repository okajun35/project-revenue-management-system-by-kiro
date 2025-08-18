from typing import Generic, List, Optional, Type, TypeVar
from app import db

T = TypeVar('T')


class BaseService(Generic[T]):
    """Generic CRUD helpers for SQLAlchemy models.

    Subclasses should set `model` or pass it to the constructor.
    These helpers are intentionally thin wrappers around SQLAlchemy
    session operations and do not include domain validation.
    """

    model: Type[T]

    def __init__(self, model: Type[T] | None = None) -> None:
        if model is not None:
            self.model = model

    # Read
    def get(self, id_: int) -> Optional[T]:  # noqa: A003 (shadow builtins)
        return self.model.query.get(id_)

    def list(self) -> List[T]:
        return self.model.query.all()

    # Write
    def add(self, instance: T) -> T:
        db.session.add(instance)
        db.session.commit()
        return instance

    def delete(self, instance: T) -> None:
        db.session.delete(instance)
        db.session.commit()
