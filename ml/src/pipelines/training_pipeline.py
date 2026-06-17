"""
ml/src/pipelines/training_pipeline.py
---------------------------------------
Orchestre le cycle complet d'entraînement :
    generate fake data → load → clean → feature engineering → train → evaluate
 
Usage :
    python -m ml.src.pipelines.training_pipeline
    python -m ml.src.pipelines.training_pipeline --source api --limit 500
    python -m ml.src.pipelines.training_pipeline --source file --path data/raw/fake_mesures.json
"""
 
import argparse
import json
from pathlib import Path
 
from ml.src.data.loader import load_combined
from ml.src.data.cleaner import clean
from ml.src.data.feature_builder import build_features
from ml.src.models.train_classifier import train_classifier
from ml.src.models.train_regressor import train_regressor
 
REPORTS_DIR = Path("ml/reports/metrics")
 
 
def run(source: str = "file", path: str = "data/raw/fake_mesures.json", limit: int = 500):
    """
    Pipeline d'entraînement complet.
 
    Args:
        source : "file" (données fake) ou "api" (données ESP32 réelles)
        path   : chemin fichier JSON si source="file"
        limit  : nombre de mesures si source="api"
    """
    print("=" * 50)
    print("🌱 TRAINING PIPELINE — Smart Irrigation IoT")
    print("=" * 50 + "\n")
 
    # ── 1. Chargement ──────────────────────────────────────────────────────────
    prefer_api = source == "api"
    df = load_combined(
        fake_path=path if not prefer_api else None,
        api_limit=limit,
        prefer_api=prefer_api,
    )
 
    if len(df) < 50:
        raise ValueError(
            f"❌ Trop peu de données ({len(df)} lignes). "
            "Génère des données avec scripts/generate_fake_data.py"
        )
 
    # ── 2. Nettoyage ───────────────────────────────────────────────────────────
    df = clean(df)
 
    # ── 3. Feature Engineering ─────────────────────────────────────────────────
    df = build_features(df)
 
    # ── 4. Entraînement ────────────────────────────────────────────────────────
    clf_metrics = train_classifier(df)
    reg_metrics = train_regressor(df)
 
    # ── 5. Rapport global ──────────────────────────────────────────────────────
    summary = {
        "dataset_size":   len(df),
        "classifier":     {
            "accuracy": clf_metrics["accuracy"],
            "model":    clf_metrics["model"],
        },
        "regressor": {
            "mae":  reg_metrics["mae"],
            "rmse": reg_metrics["rmse"],
            "r2":   reg_metrics["r2"],
            "model": reg_metrics["model"],
        },
    }
 
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(REPORTS_DIR / "training_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
 
    print("\n" + "=" * 50)
    print("🎉 ENTRAÎNEMENT TERMINÉ")
    print(f"   Classifieur  → Accuracy : {clf_metrics['accuracy']:.4f}")
    print(f"   Régresseur   → MAE : {reg_metrics['mae']:.3f}% | R² : {reg_metrics['r2']:.4f}")
    print("=" * 50)
 
    return summary