"""
backend/app/services/ingestion_service.py
----------------------------------------------
Logique métier de réception d'une mesure ESP32.
Reprend la logique du endpoint POST /mesures de Said :
    - vérifie que le capteur existe
    - enregistre la mesure
    - déclenche une irrigation automatique si humidite_sol < seuil

Dans la version de Said, tout ça était fait directement dans main.py.
Ici on l'isole dans un service pour respecter l'architecture cible.
"""

from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Mesure
from app.repositories import measurement_repository, sensor_repository, irrigation_repository
from app.schemas.measurement import MesureCreate


def ingest_mesure(db: Session, payload: MesureCreate) -> Mesure:
    """
    Traite une nouvelle mesure envoyée par l'ESP32.

    Reproduit le comportement exact de Said :
    1. Vérifie que le capteur existe (404 sinon)
    2. Crée la mesure
    3. Si humidite_sol < seuil sec → crée une irrigation automatique
    """
    capteur = sensor_repository.get_by_id(db, payload.id_capteur)
    if not capteur:
        raise HTTPException(
            status_code=404,
            detail=f"Capteur {payload.id_capteur} introuvable",
        )

    mesure = measurement_repository.create(
        db,
        id_capteur=payload.id_capteur,
        humidite_sol=payload.humidite_sol,
        temperature=payload.temperature,
        humidite_air=payload.humidite_air,
        timestamp=datetime.now(),
    )

    # Irrigation automatique si sol sec (même seuil que le générateur ML : 30%)
    if payload.humidite_sol < settings.SOIL_DRY_THRESHOLD:
        irrigation_repository.create(
            db,
            id_parcelle=capteur.id_parcelle,
            volume_eau=0.0,
            mode="automatique",
        )

    return mesure
