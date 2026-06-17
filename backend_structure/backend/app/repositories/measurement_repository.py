"""
backend/app/repositories/measurement_repository.py
-------------------------------------------------------
Couche d'accès aux données pour Mesure.
Isole les requêtes SQLAlchemy du code métier (services/).
"""

from sqlalchemy.orm import Session

from app.db.models import Mesure


def create(db: Session, *, id_capteur: int, humidite_sol: float,
           temperature: float, humidite_air: float | None, timestamp) -> Mesure:
    mesure = Mesure(
        id_capteur=id_capteur,
        humidite_sol=humidite_sol,
        temperature=temperature,
        humidite_air=humidite_air,
        timestamp=timestamp,
    )
    db.add(mesure)
    db.commit()
    db.refresh(mesure)
    return mesure


def get_by_id(db: Session, id_mesure: int) -> Mesure | None:
    return db.query(Mesure).filter(Mesure.id_mesure == id_mesure).first()


def list_recent(db: Session, limit: int = 50) -> list[Mesure]:
    return (
        db.query(Mesure)
        .order_by(Mesure.timestamp.desc())
        .limit(limit)
        .all()
    )


def count(db: Session) -> int:
    return db.query(Mesure).count()


def get_latest(db: Session) -> Mesure | None:
    return db.query(Mesure).order_by(Mesure.timestamp.desc()).first()
