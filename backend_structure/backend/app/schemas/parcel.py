"""
backend/app/schemas/parcel.py
--------------------------------
Schémas Pydantic : Parcelle.
"""

from typing import Optional

from pydantic import BaseModel


class ParcelleCreate(BaseModel):
    nom:          str
    superficie:   Optional[float] = None
    type_culture: Optional[str]   = None
    localisation: Optional[str]   = None


class ParcelleOut(ParcelleCreate):
    id_parcelle: int

    class Config:
        from_attributes = True
