"""
backend/app/schemas/measurement.py
-------------------------------------
Schémas Pydantic : Mesure.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MesureCreate(BaseModel):
    id_capteur:   int
    humidite_sol: float
    temperature:  float
    humidite_air: Optional[float] = None


class MesureOut(MesureCreate):
    id_mesure: int
    timestamp: datetime

    class Config:
        from_attributes = True
