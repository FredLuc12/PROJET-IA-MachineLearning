"""
backend/app/db/models/irrigation_model.py
----------------------------------------------
Modèle SQLAlchemy : Irrigation.
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.db.base import Base


class Irrigation(Base):
    __tablename__ = "irrigation"

    id_irrigation = Column(Integer, primary_key=True, index=True)
    id_parcelle   = Column(Integer, ForeignKey("parcelle.id_parcelle"))
    date_debut    = Column(DateTime, server_default=func.now())
    date_fin      = Column(DateTime)
    volume_eau    = Column(Float)
    mode          = Column(String(20), default="automatique")
