"""
backend/app/repositories/sensor_repository.py
----------------------------------------------------
Couche d'accès aux données pour Capteur.
"""

from sqlalchemy.orm import Session

from app.db.models import Capteur


def get_by_id(db: Session, id_capteur: int) -> Capteur | None:
    return db.query(Capteur).filter(Capteur.id_capteur == id_capteur).first()


def list_all(db: Session) -> list[Capteur]:
    return db.query(Capteur).all()
