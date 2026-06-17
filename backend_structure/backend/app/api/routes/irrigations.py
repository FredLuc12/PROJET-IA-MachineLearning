"""
backend/app/api/routes/irrigations.py
--------------------------------------------
Endpoints liés aux Irrigations.
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.irrigation import IrrigationOut
from app.services import irrigation_service

router = APIRouter(prefix="/irrigations", tags=["Irrigations"])


@router.get("", response_model=List[IrrigationOut])
def get_irrigations(db: Session = Depends(get_db)):
    return irrigation_service.list_recent_irrigations(db, limit=20)
