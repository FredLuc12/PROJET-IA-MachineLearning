"""
backend/app/db/models/sensor_model.py
----------------------------------------
Modèle SQLAlchemy : Capteur.
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.db.base import Base


class Capteur(Base):
    __tablename__ = "capteur"

    id_capteur   = Column(Integer, primary_key=True, index=True)
    id_parcelle  = Column(Integer, ForeignKey("parcelle.id_parcelle"))
    type_capteur = Column(String(50), nullable=False)
    date_install = Column(DateTime, server_default=func.now())
    statut       = Column(String(20), default="actif")
    profondeur   = Column(Float)
