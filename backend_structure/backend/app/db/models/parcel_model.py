"""
backend/app/db/models/parcel_model.py
----------------------------------------
Modèle SQLAlchemy : Parcelle.
"""

from sqlalchemy import Column, Integer, Float, String

from app.db.base import Base


class Parcelle(Base):
    __tablename__ = "parcelle"

    id_parcelle  = Column(Integer, primary_key=True, index=True)
    nom          = Column(String(100), nullable=False)
    superficie   = Column(Float)
    type_culture = Column(String(50))
    localisation = Column(String(150))
