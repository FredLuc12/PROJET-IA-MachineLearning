"""
backend/app/schemas/sensor.py
--------------------------------
Schémas Pydantic : Capteur.
"""

from pydantic import BaseModel


class CapteurOut(BaseModel):
    id_capteur:   int
    id_parcelle:  int
    type_capteur: str
    statut:       str

    class Config:
        from_attributes = True
