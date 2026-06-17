"""
backend/app/api/routes/recommendations.py
-------------------------------------------------
Endpoints liés aux Recommandations ML.
C'EST ICI que ton pipeline d'inférence (ml/src/pipelines/inference_pipeline.py)
envoie ses prédictions via POST /recommandations?id_mesure=...&besoin_eau=...
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.recommendation import RecommandationOut
from app.services import recommendation_service

router = APIRouter(prefix="/recommandations", tags=["Recommandations ML"])


@router.post("", response_model=RecommandationOut, status_code=201)
def create_recommandation(
    id_mesure: int,
    besoin_eau: bool,
    niveau_humidite_prevu: float,
    modele_utilise: str,
    db: Session = Depends(get_db),
):
    """
    Reçoit une recommandation produite par le pipeline ML (RandomForest).
    Appelé par : ml/src/pipelines/inference_pipeline.py::post_recommendation()
    """
    return recommendation_service.create_recommendation(
        db,
        id_mesure=id_mesure,
        besoin_eau=besoin_eau,
        niveau_humidite_prevu=niveau_humidite_prevu,
        modele_utilise=modele_utilise,
    )


@router.get("", response_model=List[RecommandationOut])
def get_recommandations(db: Session = Depends(get_db)):
    return recommendation_service.list_recent_recommendations(db, limit=20)
