"""
backend/app/api/routes/health.py
--------------------------------------
Endpoint racine + healthcheck + stats globales.
Reprend les routes "/" et "/stats" du main.py de Said.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.repositories import measurement_repository, irrigation_repository, recommendation_repository

router = APIRouter(tags=["Health"])


@router.get("/")
def root():
    return {
        "projet":  "HydroSmart",
        "status":  "ok",
        "version": settings.APP_VERSION,
    }


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    derniere = measurement_repository.get_latest(db)
    return {
        "total_mesures":      measurement_repository.count(db),
        "total_irrigations":  irrigation_repository.count(db),
        "total_recos_ml":     recommendation_repository.count(db),
        "derniere_mesure": {
            "temperature":   derniere.temperature  if derniere else None,
            "humidite_sol":  derniere.humidite_sol  if derniere else None,
            "humidite_air":  derniere.humidite_air  if derniere else None,
            "timestamp":     str(derniere.timestamp) if derniere else None,
        },
    }
