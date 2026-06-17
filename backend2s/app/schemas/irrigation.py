# hydrosmart/api/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MesureCreate(BaseModel):
    id_capteur   : int
    humidite_sol : float
    temperature  : float
    humidite_air : Optional[float] = None

class MesureOut(MesureCreate):
    id_mesure : int
    timestamp : datetime
    class Config:
        from_attributes = True

class ParcelleCreate(BaseModel):
    nom          : str
    superficie   : Optional[float] = None
    type_culture : Optional[str]   = None
    localisation : Optional[str]   = None

class ParcelleOut(ParcelleCreate):
    id_parcelle : int
    class Config:
        from_attributes = True

class CapteurOut(BaseModel):
    id_capteur   : int
    id_parcelle  : int
    type_capteur : str
    statut       : str
    class Config:
        from_attributes = True

class RecommandationOut(BaseModel):
    id_recommandation     : int
    id_mesure             : int
    timestamp             : datetime
    besoin_eau            : bool
    niveau_humidite_prevu : float
    modele_utilise        : str
    class Config:
        from_attributes = True