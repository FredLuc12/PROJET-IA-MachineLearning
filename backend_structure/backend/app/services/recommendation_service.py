"""
backend/app/services/recommendation_service.py
-----------------------------------------------------
Logique métier de réception des recommandations ML.
C'est CE service qui reçoit les appels de ton pipeline d'inférence
(ml/src/pipelines/inference_pipeline.py → POST /recommandations).
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models import RecommandationML
from app.repositories import recommendation_repository, measurement_repository


def create_recommendation(
    db: Session,
    *,
    id_mesure: int,
    besoin_eau: bool,
    niveau_humidite_prevu: float,
    modele_utilise: str,
) -> RecommandationML:
    """
    Enregistre une recommandation produite par le pipeline ML.
    Vérifie que la mesure référencée existe.
    """
    mesure = measurement_repository.get_by_id(db, id_mesure)
    if not mesure:
        raise HTTPException(
            status_code=404,
            detail=f"Mesure {id_mesure} introuvable — impossible de créer la recommandation",
        )

    return recommendation_repository.create(
        db,
        id_mesure=id_mesure,
        besoin_eau=besoin_eau,
        niveau_humidite_prevu=niveau_humidite_prevu,
        modele_utilise=modele_utilise,
    )


def list_recent_recommendations(db: Session, limit: int = 20) -> list[RecommandationML]:
    return recommendation_repository.list_recent(db, limit=limit)
