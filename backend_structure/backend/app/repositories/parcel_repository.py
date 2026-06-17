"""
backend/app/repositories/parcel_repository.py
----------------------------------------------------
Couche d'accès aux données pour Parcelle.
"""

from sqlalchemy.orm import Session

from app.db.models import Parcelle


def create(db: Session, *, nom: str, superficie: float | None,
           type_culture: str | None, localisation: str | None) -> Parcelle:
    parcelle = Parcelle(
        nom=nom, superficie=superficie,
        type_culture=type_culture, localisation=localisation,
    )
    db.add(parcelle)
    db.commit()
    db.refresh(parcelle)
    return parcelle


def list_all(db: Session) -> list[Parcelle]:
    return db.query(Parcelle).all()


def get_by_id(db: Session, id_parcelle: int) -> Parcelle | None:
    return db.query(Parcelle).filter(Parcelle.id_parcelle == id_parcelle).first()
