"""
backend/app/api/routes/measurements.py
-------------------------------------------
Endpoints liés aux Mesures.
Équivalent des routes /mesures et /mesures/{id} du main.py de Said.
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.measurement import MesureCreate, MesureOut
from app.services import ingestion_service, measurement_service

router = APIRouter(prefix="/mesures", tags=["Mesures"])


@router.post("", response_model=MesureOut, status_code=201)
def create_mesure(payload: MesureCreate, db: Session = Depends(get_db)):
    """Reçoit une mesure depuis l'ESP32 (firmware/esp32/esp32_irrigation.ino)."""
    return ingestion_service.ingest_mesure(db, payload)


@router.get("", response_model=List[MesureOut])
def get_mesures(limit: int = 50, db: Session = Depends(get_db)):
    return measurement_service.list_recent_mesures(db, limit=limit)


@router.get("/{id_mesure}", response_model=MesureOut)
def get_mesure(id_mesure: int, db: Session = Depends(get_db)):
    return measurement_service.get_mesure_or_404(db, id_mesure)
