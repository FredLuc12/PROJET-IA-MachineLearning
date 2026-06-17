"""
backend/app/db/models/recommendation_model.py
----------------------------------------------------
Modèle SQLAlchemy : RecommandationML.
C'est CE modèle que ton ML va alimenter via POST /recommandations.
"""

from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.db.base import Base


class RecommandationML(Base):
    __tablename__ = "recommandation_ml"

    id_recommandation     = Column(Integer, primary_key=True, index=True)
    id_mesure              = Column(Integer, ForeignKey("mesure.id_mesure"))
    id_irrigation          = Column(Integer, ForeignKey("irrigation.id_irrigation"), nullable=True)
    timestamp              = Column(DateTime, server_default=func.now())
    besoin_eau             = Column(Boolean)
    niveau_humidite_prevu  = Column(Float)
    modele_utilise         = Column(String(100))
