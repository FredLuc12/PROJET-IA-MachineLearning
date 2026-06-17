"""
backend/app/services/irrigation_service.py
----------------------------------------------
Logique métier liée aux irrigations.
"""

from sqlalchemy.orm import Session

from app.db.models import Irrigation
from app.repositories import irrigation_repository


def list_recent_irrigations(db: Session, limit: int = 20) -> list[Irrigation]:
    return irrigation_repository.list_recent(db, limit=limit)
