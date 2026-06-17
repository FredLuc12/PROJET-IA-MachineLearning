"""
backend/app/api/routes/parcels.py
--------------------------------------
Endpoints liés aux Parcelles.
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories import parcel_repository
from app.schemas.parcel import ParcelleCreate, ParcelleOut

router = APIRouter(prefix="/parcelles", tags=["Parcelles"])


@router.get("", response_model=List[ParcelleOut])
def get_parcelles(db: Session = Depends(get_db)):
    return parcel_repository.list_all(db)


@router.post("", response_model=ParcelleOut, status_code=201)
def create_parcelle(payload: ParcelleCreate, db: Session = Depends(get_db)):
    return parcel_repository.create(
        db,
        nom=payload.nom,
        superficie=payload.superficie,
        type_culture=payload.type_culture,
        localisation=payload.localisation,
    )
