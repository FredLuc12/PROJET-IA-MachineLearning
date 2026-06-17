"""
scripts/seed_db.py
-------------------
Peuple la base de données de Said en envoyant des mesures fake via son API.
Utile pour avoir des données de démo sans attendre l'ESP32.

Usage :
    python scripts/seed_db.py
    python scripts/seed_db.py --days 7 --interval 300 --batch 50
"""

import argparse
import json
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.generate_fake_data import generate_dataset

API_BASE_URL = "http://localhost:8000"


def post_mesure(session: requests.Session, mesure: dict) -> bool:
    """Envoie une mesure vers POST /mesures (si l'endpoint existe)."""
    url = f"{API_BASE_URL}/mesures"
    payload = {
        "id_capteur":   mesure["id_capteur"],
        "timestamp":    mesure["timestamp"],
        "humidite_sol": mesure["humidite_sol"],
        "temperature":  mesure["temperature"],
        "humidite_air": mesure["humidite_air"],
    }
    try:
        resp = session.post(url, json=payload, timeout=5)
        resp.raise_for_status()
        return True
    except requests.exceptions.HTTPError as e:
        print(f"   ⚠️  HTTP {e.response.status_code} : {e}")
        return False
    except Exception as e:
        print(f"   ⚠️  Erreur : {e}")
        return False


def seed(days: int = 7, interval: int = 300, batch_size: int = 50, delay: float = 0.05):
    """
    Génère et envoie des mesures à l'API.

    Args:
        days       : jours de données à générer
        interval   : secondes entre mesures
        batch_size : mesures affichées par log
        delay      : délai entre requêtes (évite de flood l'API)
    """
    print(f"🌱 Génération de {days} jours de données (intervalle {interval}s)...")
    records = generate_dataset(days=days, interval_seconds=interval)
    total   = len(records)
    print(f"📦 {total} mesures à envoyer vers {API_BASE_URL}\n")

    session = requests.Session()
    success = 0
    errors  = 0

    for i, record in enumerate(records):
        ok = post_mesure(session, record)
        if ok:
            success += 1
        else:
            errors += 1

        if (i + 1) % batch_size == 0 or (i + 1) == total:
            pct = (i + 1) / total * 100
            print(f"   [{i+1}/{total}] {pct:.1f}% — ✅ {success} | ❌ {errors}")

        time.sleep(delay)

    print(f"\n🎉 Seed terminé — {success}/{total} mesures insérées")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--days",     type=int,   default=7)
    parser.add_argument("--interval", type=int,   default=300,
                        help="Secondes entre mesures (défaut: 300 = 5min)")
    parser.add_argument("--batch",    type=int,   default=50)
    parser.add_argument("--delay",    type=float, default=0.05,
                        help="Délai entre requêtes en secondes")
    args = parser.parse_args()
    seed(days=args.days, interval=args.interval, batch_size=args.batch, delay=args.delay)