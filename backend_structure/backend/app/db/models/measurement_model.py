"""
backend/app/db/models/measurement_model.py
----------------------------------------------
Modèle SQLAlchemy : Mesure.
"""

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.db.base import Base


class Mesure(Base):
    __tablename__ = "mesure"

    id_mesure    = Column(Integer, primary_key=True, index=True)
    id_capteur   = Column(Integer, ForeignKey("capteur.id_capteur"))
    timestamp    = Column(DateTime, server_default=func.now())
    humidite_sol = Column(Float)
    temperature  = Column(Float)
    humidite_air = Column(Float)
