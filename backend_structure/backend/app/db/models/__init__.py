"""
backend/app/db/models/__init__.py
------------------------------------
Réexporte tous les modèles pour qu'Alembic les détecte (autogenerate)
et pour simplifier les imports ailleurs : `from app.db.models import Mesure`.
"""

from app.db.models.parcel_model import Parcelle
from app.db.models.sensor_model import Capteur
from app.db.models.measurement_model import Mesure
from app.db.models.irrigation_model import Irrigation
from app.db.models.recommendation_model import RecommandationML

__all__ = [
    "Parcelle",
    "Capteur",
    "Mesure",
    "Irrigation",
    "RecommandationML",
]
