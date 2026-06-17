"""
backend/app/services/measurement_service.py
----------------------------------------------
Logique métier de lecture des mesures (GET endpoints).
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models import Mesure
from app.repositories import measurement_repository


def get_mesure_or_404(db: Session, id_mesure: int) -> Mesure:
    mesure = measurement_repository.get_by_id(db, id_mesure)
    if not mesure:
        raise HTTPException(status_code=404, detail="Mesure introuvable")
    return mesure


def list_recent_mesures(db: Session, limit: int = 50) -> list[Mesure]:
    return measurement_repository.list_recent(db, limit=limit)
