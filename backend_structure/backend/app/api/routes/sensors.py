"""
backend/app/api/routes/sensors.py
--------------------------------------
Endpoints liés aux Capteurs.
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories import sensor_repository
from app.schemas.sensor import CapteurOut

router = APIRouter(prefix="/capteurs", tags=["Capteurs"])


@router.get("", response_model=List[CapteurOut])
def get_capteurs(db: Session = Depends(get_db)):
    return sensor_repository.list_all(db)
