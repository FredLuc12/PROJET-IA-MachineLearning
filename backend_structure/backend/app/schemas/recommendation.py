"""
backend/app/schemas/recommendation.py
-----------------------------------------
Schémas Pydantic : RecommandationML.
C'est le schéma que ton pipeline d'inférence ML cible via POST /recommandations.
"""

from datetime import datetime

from pydantic import BaseModel


class RecommandationOut(BaseModel):
    id_recommandation:      int
    id_mesure:               int
    timestamp:                datetime
    besoin_eau:               bool
    niveau_humidite_prevu:    float
    modele_utilise:           str

    class Config:
        from_attributes = True
