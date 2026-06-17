"""
backend/app/repositories/irrigation_repository.py
----------------------------------------------------
Couche d'accès aux données pour Irrigation.
"""

from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import Irrigation


def create(db: Session, *, id_parcelle: int, volume_eau: float = 0.0,
           mode: str = "automatique") -> Irrigation:
    irrigation = Irrigation(
        id_parcelle=id_parcelle,
        date_debut=datetime.now(),
        volume_eau=volume_eau,
        mode=mode,
    )
    db.add(irrigation)
    db.commit()
    db.refresh(irrigation)
    return irrigation


def list_recent(db: Session, limit: int = 20) -> list[Irrigation]:
    return (
        db.query(Irrigation)
        .order_by(Irrigation.date_debut.desc())
        .limit(limit)
        .all()
    )


def count(db: Session) -> int:
    return db.query(Irrigation).count()
