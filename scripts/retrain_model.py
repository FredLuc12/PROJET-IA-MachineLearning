"""
scripts/retrain_model.py
-------------------------
Raccourci pour relancer le cycle complet d'entraînement.
Peut utiliser les données API réelles ou le fichier fake local.

Usage :
    # Réentraîner sur fake data (défaut)
    python scripts/retrain_model.py

    # Réentraîner sur données réelles de l'ESP32
    python scripts/retrain_model.py --source api --limit 500

    # Regénérer les fake data puis réentraîner
    python scripts/retrain_model.py --regen --days 30
"""

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

FAKE_DATA_PATH = "data/raw/fake_mesures.json"


def regen_fake_data(days: int, interval: int):
    """Regénère les données simulées."""
    print(f"🔄 Régénération des données fake ({days} jours)...")
    cmd = [
        sys.executable, "scripts/generate_fake_data.py",
        "--days",     str(days),
        "--interval", str(interval),
        "--output",   FAKE_DATA_PATH,
    ]
    result = subprocess.run(cmd, check=True)
    if result.returncode != 0:
        raise RuntimeError("❌ Échec de la génération de données")


def retrain(source: str = "file", limit: int = 500):
    """Lance le training pipeline."""
    from ml.src.pipelines.training_pipeline import run
    return run(source=source, path=FAKE_DATA_PATH, limit=limit)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Réentraîne les modèles ML")
    parser.add_argument("--source",   choices=["file", "api"], default="file",
                        help="Source de données : fake (file) ou ESP32 (api)")
    parser.add_argument("--limit",    type=int, default=500,
                        help="Nombre de mesures si source=api")
    parser.add_argument("--regen",    action="store_true",
                        help="Regénère les données fake avant d'entraîner")
    parser.add_argument("--days",     type=int, default=30,
                        help="Jours de données fake si --regen")
    parser.add_argument("--interval", type=int, default=300,
                        help="Intervalle mesures en secondes si --regen")
    args = parser.parse_args()

    if args.regen:
        regen_fake_data(days=args.days, interval=args.interval)

    summary = retrain(source=args.source, limit=args.limit)

    print("\n📋 Résumé :")
    print(f"   Classifieur → Accuracy : {summary['classifier']['accuracy']:.4f}")
    print(f"   Régresseur  → MAE : {summary['regressor']['mae']:.3f}%  R² : {summary['regressor']['r2']:.4f}")