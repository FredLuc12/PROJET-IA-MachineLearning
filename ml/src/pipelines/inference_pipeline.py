"""
ml/src/pipelines/inference_pipeline.py
----------------------------------------
Pipeline d'inférence :
1. Récupère les dernières mesures depuis GET /mesures
2. Construit les features
3. Prédit l'état du sol (classifieur) et l'humidité future (régresseur)
4. Poste les recommandations vers POST /recommandations
 
Usage :
    python -m ml.src.pipelines.inference_pipeline
    python -m ml.src.pipelines.inference_pipeline --limit 100 --dry-run
"""
 
import argparse
import os
from pathlib import Path
 
import joblib
import numpy as np
import pandas as pd
import requests
 
from ml.src.data.cleaner import clean
from ml.src.data.feature_builder import build_features, get_feature_columns
from ml.src.data.loader import fetch_mesures_from_api
 
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
MODELS_DIR   = Path("ml/models")
 
MODEL_NAME = "RandomForest"
 
 
def load_models() -> tuple:
    """Charge classifier, regressor, scaler, label_encoder."""
    clf     = joblib.load(MODELS_DIR / "classifier.joblib")
    reg     = joblib.load(MODELS_DIR / "regressor.joblib")
    scaler  = joblib.load(MODELS_DIR / "scaler.joblib")
    le      = joblib.load(MODELS_DIR / "label_encoder.joblib")
    scaler_reg = joblib.load(MODELS_DIR / "scaler_reg.joblib")
    return clf, reg, scaler, le, scaler_reg
 
 
def predict(df: pd.DataFrame, clf, reg, scaler, le, scaler_reg) -> pd.DataFrame:
    """
    Ajoute les colonnes de prédiction au DataFrame.
    Retourne le DataFrame avec 'pred_etat_sol', 'pred_besoin_eau', 'pred_humidite'.
    """
    cols         = get_feature_columns()
    feature_cols = cols["features"]
 
    X = df[feature_cols].values
 
    # Classification
    X_scaled_clf          = scaler.transform(X)
    pred_class_enc        = clf.predict(X_scaled_clf)
    pred_etat_sol         = le.inverse_transform(pred_class_enc)
    pred_besoin_eau       = pred_etat_sol == "sec"
 
    # Régression
    X_scaled_reg          = scaler_reg.transform(X)
    pred_humidite         = reg.predict(X_scaled_reg).round(1)
    pred_humidite         = np.clip(pred_humidite, 0.0, 100.0)
 
    df = df.copy()
    df["pred_etat_sol"]   = pred_etat_sol
    df["pred_besoin_eau"] = pred_besoin_eau
    df["pred_humidite"]   = pred_humidite
 
    return df
 
 
def post_recommendation(
    id_mesure: int,
    besoin_eau: bool,
    humidite_prevue: float,
    dry_run: bool = False,
) -> dict | None:
    """
    Envoie une recommandation ML vers POST /recommandations.
    dry_run=True → affiche sans envoyer.
    """
    params = {
        "id_mesure":            id_mesure,
        "besoin_eau":           str(besoin_eau).lower(),  # "true" / "false"
        "niveau_humidite_prevu": humidite_prevue,
        "modele_utilise":       MODEL_NAME,
    }
 
    if dry_run:
        print(f"   [dry-run] POST /recommandations params={params}")
        return None
 
    url = f"{API_BASE_URL}/recommandations"
    response = requests.post(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()
 
 
def run(limit: int = 100, dry_run: bool = False):
    """Pipeline complet : fetch → predict → post."""
    print("🚀 Inference pipeline démarré\n")
 
    # ── 1. Chargement ──────────────────────────────────────────────────────────
    df_raw = fetch_mesures_from_api(limit=limit)
 
    # ── 2. Nettoyage + features ────────────────────────────────────────────────
    df = clean(df_raw)
    df = build_features(df)
 
    # ── 3. Prédictions ─────────────────────────────────────────────────────────
    clf, reg, scaler, le, scaler_reg = load_models()
    df = predict(df, clf, reg, scaler, le, scaler_reg)
 
    # ── 4. Envoi des recommandations ───────────────────────────────────────────
    print(f"📤 Envoi de {len(df)} recommandations vers l'API...")
    success = 0
    errors  = 0
 
    for _, row in df.iterrows():
        try:
            result = post_recommendation(
                id_mesure       = int(row["id_mesure"]),
                besoin_eau      = bool(row["pred_besoin_eau"]),
                humidite_prevue = float(row["pred_humidite"]),
                dry_run         = dry_run,
            )
            success += 1
        except Exception as e:
            print(f"   ⚠️  Erreur mesure {row.get('id_mesure')} : {e}")
            errors += 1
 
    print(f"\n✅ Terminé — succès: {success} | erreurs: {errors}")
 
    # ── Résumé des prédictions ─────────────────────────────────────────────────
    print("\n📊 Résumé prédictions :")
    print(df["pred_etat_sol"].value_counts().to_string())
    print(f"   💧 Besoin eau : {df['pred_besoin_eau'].sum()} / {len(df)}")
    print(f"   📉 Humidité prévue moyenne : {df['pred_humidite'].mean():.1f}%")
 
    return df
 
 
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit",   type=int,  default=100)
    parser.add_argument("--dry-run", action="store_true",
                        help="Prédit sans envoyer à l'API")
    args = parser.parse_args()
    run(limit=args.limit, dry_run=args.dry_run)