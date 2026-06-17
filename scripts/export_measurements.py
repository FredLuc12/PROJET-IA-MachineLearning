"""
scripts/export_measurements.py
--------------------------------
Exporte les mesures depuis l'API de Said vers un fichier CSV.
Utile pour l'analyse offline ou le réentraînement du modèle.

Usage :
    python scripts/export_measurements.py
    python scripts/export_measurements.py --limit 1000 --output data/exports/mesures.csv
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from ml.src.data.loader import fetch_mesures_from_api


def export(limit: int = 500, output: str = "data/exports/mesures.csv"):
    """
    Récupère les mesures depuis l'API et les exporte en CSV.

    Args:
        limit  : nombre de mesures à récupérer
        output : chemin du fichier CSV de sortie
    """
    print(f"📥 Récupération de {limit} mesures depuis l'API...")
    df = fetch_mesures_from_api(limit=limit)

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_path, index=False, encoding="utf-8")

    print(f"✅ {len(df)} mesures exportées → {output_path}")
    print(f"\n   Période : {df['timestamp'].min()} → {df['timestamp'].max()}")
    print(f"   Colonnes : {list(df.columns)}")
    print(f"\n   Aperçu :")
    print(df[["timestamp", "humidite_sol", "temperature", "humidite_air"]].head(5).to_string(index=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit",  type=int, default=500)
    parser.add_argument("--output", type=str,
                        default=f"data/exports/mesures_{datetime.now().strftime('%Y%m%d_%H%M')}.csv")
    args = parser.parse_args()
    export(limit=args.limit, output=args.output)