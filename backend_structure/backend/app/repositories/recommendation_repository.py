"""
backend/app/repositories/recommendation_repository.py
-------------------------------------------------------------
Couche d'accès aux données pour RecommandationML.
C'est ici que les recommandations envoyées par ton pipeline ML sont
finalement persistées en base.
"""

from sqlalchemy.orm import Session

from app.db.models import RecommandationML


def create(db: Session, *, id_mesure: int, besoin_eau: bool,
           niveau_humidite_prevu: float, modele_utilise: str,
           id_irrigation: int | None = None) -> RecommandationML:
    reco = RecommandationML(
        id_mesure=id_mesure,
        id_irrigation=id_irrigation,
        besoin_eau=besoin_eau,
        niveau_humidite_prevu=niveau_humidite_prevu,
        modele_utilise=modele_utilise,
    )
    db.add(reco)
    db.commit()
    db.refresh(reco)
    return reco


def list_recent(db: Session, limit: int = 20) -> list[RecommandationML]:
    return (
        db.query(RecommandationML)
        .order_by(RecommandationML.timestamp.desc())
        .limit(limit)
        .all()
    )


def count(db: Session) -> int:
    return db.query(RecommandationML).count()
