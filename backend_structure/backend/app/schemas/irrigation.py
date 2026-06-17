"""
backend/app/schemas/irrigation.py
------------------------------------
Schémas Pydantic : Irrigation.
Absent du schemas.py original de Said (il renvoyait le modèle SQLAlchemy
brut dans /irrigations) — ajouté ici pour cohérence avec le reste de l'API.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class IrrigationOut(BaseModel):
    id_irrigation: int
    id_parcelle:   int
    date_debut:    datetime
    date_fin:      Optional[datetime] = None
    volume_eau:    float
    mode:          str

    class Config:
        from_attributes = True
