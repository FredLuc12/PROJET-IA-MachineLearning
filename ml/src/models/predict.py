"""
ml/src/models/predict.py
-------------------------
Prédiction unitaire sur une seule mesure (dict ou ligne DataFrame).
Utilisé par le recommendation_engine et l'API ML.
 
Usage :
    from ml.src.models.predict import predict_single
 
    result = predict_single({
        "humidite_sol": 15.2,
        "temperature":  29.5,
        "humidite_air": 48.0,
        "timestamp":    "2026-06-16T14:32:05",
    })
    # → {"etat_sol": "sec", "besoin_eau": True, "humidite_prevue": 12.4}
"""
 
from datetime import datetime
from pathlib import Path
from typing import Union
 
import joblib
import numpy as np
import pandas as pd
 
from ml.src.data.feature_builder import build_features, get_feature_columns
 
MODELS_DIR = Path("ml/models")
 
 
def _load_models():
    """Charge tous les artefacts ML depuis ml/models/."""
    return {
        "clf":        joblib.load(MODELS_DIR / "classifier.joblib"),
        "reg":        joblib.load(MODELS_DIR / "regressor.joblib"),
        "scaler":     joblib.load(MODELS_DIR / "scaler.joblib"),
        "le":         joblib.load(MODELS_DIR / "label_encoder.joblib"),
        "scaler_reg": joblib.load(MODELS_DIR / "scaler_reg.joblib"),
    }
 
 
# Cache des modèles (chargés une seule fois)
_MODELS: dict | None = None
 
 
def _get_models() -> dict:
    global _MODELS
    if _MODELS is None:
        _MODELS = _load_models()
    return _MODELS
 
 
def predict_single(
    mesure: Union[dict, pd.Series],
    reload_models: bool = False,
) -> dict:
    """
    Prédit l'état du sol et l'humidité future pour une seule mesure.
 
    Args:
        mesure : dict ou Series avec au minimum :
                 humidite_sol, temperature, humidite_air, timestamp
        reload_models : force le rechargement des fichiers .joblib
 
    Returns:
        {
            "etat_sol":       "sec" | "normal" | "humide",
            "besoin_eau":     True | False,
            "humidite_prevue": float (%)
        }
    """
    global _MODELS
    if reload_models:
        _MODELS = None
 
    models = _get_models()
    cols   = get_feature_columns()
    feature_cols = cols["features"]
 
    # ── Construire un mini-DataFrame pour le feature builder ──────────────────
    if isinstance(mesure, dict):
        row = mesure.copy()
    else:
        row = mesure.to_dict()
 
    # Valeurs par défaut pour les colonnes optionnelles
    row.setdefault("etat_sol",        None)
    row.setdefault("besoin_eau",      None)
    row.setdefault("humidite_prevue", None)
    row.setdefault("irrigated",       False)
    row.setdefault("id_mesure",       0)
    row.setdefault("id_capteur",      1)
 
    if "timestamp" not in row:
        row["timestamp"] = datetime.now().isoformat()
 
    df = pd.DataFrame([row])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
 
    # ── Feature engineering (time + rolling minimal sur 1 ligne) ─────────────
    df = build_features(df)
 
    # Colonnes manquantes après rolling (1 seule ligne → rolling trivial)
    for col in feature_cols:
        if col not in df.columns:
            df[col] = 0.0
 
    X = df[feature_cols].values
 
    # ── Classification ────────────────────────────────────────────────────────
    X_clf     = models["scaler"].transform(X)
    pred_enc  = models["clf"].predict(X_clf)[0]
    etat_sol  = models["le"].inverse_transform([pred_enc])[0]
    besoin_eau = etat_sol == "sec"
 
    # ── Régression ────────────────────────────────────────────────────────────
    X_reg          = models["scaler_reg"].transform(X)
    humidite_prevue = float(np.clip(models["reg"].predict(X_reg)[0], 0.0, 100.0))
 
    return {
        "etat_sol":        etat_sol,
        "besoin_eau":      besoin_eau,
        "humidite_prevue": round(humidite_prevue, 1),
    }
 
 
if __name__ == "__main__":
    result = predict_single({
        "humidite_sol": 15.0,
        "temperature":  30.0,
        "humidite_air": 45.0,
        "timestamp":    datetime.now().isoformat(),
    })
    print(result)