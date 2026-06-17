
"""
ml/src/data/loader.py
---------------------
Charge les données depuis l'API backend (Said) ou depuis un fichier local.
Retourne toujours un DataFrame pandas normalisé.
"""
 
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional
 
import pandas as pd
import requests
 
# URL de base de l'API (via variable d'environnement ou défaut local)
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
 
 
# ── Chargement depuis l'API ────────────────────────────────────────────────────
 
def fetch_mesures_from_api(limit: int = 500) -> pd.DataFrame:
    """
    Récupère les mesures depuis GET /mesures?limit=N
    Retourne un DataFrame brut.
    """
    url = f"{API_BASE_URL}/mesures"
    params = {"limit": limit}
 
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        print(f"✅ {len(data)} mesures récupérées depuis l'API")
        return _normalize_mesures(data)
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            f"❌ Impossible de joindre l'API à {url}. "
            "Vérifie que le backend tourne ou utilise load_from_file()."
        )
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"❌ Erreur HTTP : {e}")
 
 
def fetch_irrigations_from_api() -> pd.DataFrame:
    """
    Récupère les irrigations depuis GET /irrigations
    Retourne un DataFrame.
    """
    url = f"{API_BASE_URL}/irrigations"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        print(f"✅ {len(data)} irrigations récupérées depuis l'API")
        return pd.DataFrame(data)
    except requests.exceptions.ConnectionError:
        raise ConnectionError(f"❌ Impossible de joindre l'API à {url}.")
 
 
def fetch_stats_from_api() -> dict:
    """Récupère GET /stats pour un aperçu rapide."""
    url = f"{API_BASE_URL}/stats"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()
 
 
# ── Chargement depuis fichier local ───────────────────────────────────────────
 
def load_from_file(path: str | Path) -> pd.DataFrame:
    """
    Charge des mesures depuis un fichier JSON local (ex: fake_mesures.json).
    Compatible avec le format généré par generate_fake_data.py ET le format API.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"❌ Fichier introuvable : {path}")
 
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
 
    print(f"✅ {len(data)} mesures chargées depuis {path}")
    return _normalize_mesures(data)
 
 
# ── Normalisation commune ──────────────────────────────────────────────────────
 
def _normalize_mesures(data: list[dict]) -> pd.DataFrame:
    """
    Normalise une liste de mesures (API ou fichier) en DataFrame propre.
    Garantit les types corrects et les colonnes attendues.
    """
    df = pd.DataFrame(data)
 
    # Parsing timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"])
 
    # Cast types numériques
    numeric_cols = ["humidite_sol", "temperature", "humidite_air"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
 
    # Colonnes attendues (présentes dans fake data, absentes des données API réelles)
    optional_label_cols = ["etat_sol", "besoin_eau", "humidite_prevue", "irrigated", "hour"]
    for col in optional_label_cols:
        if col not in df.columns:
            df[col] = None  # sera rempli par feature_builder.py
 
    # Tri chronologique
    df = df.sort_values("timestamp").reset_index(drop=True)
 
    return df
 
 
# ── Chargement combiné (API réelle + fake pour entraînement) ──────────────────
 
def load_combined(
    fake_path: Optional[str | Path] = None,
    api_limit: int = 500,
    prefer_api: bool = True,
) -> pd.DataFrame:
    """
    Stratégie de chargement flexible :
    - Si prefer_api=True, tente l'API d'abord, fallback sur fichier local
    - Sinon, charge uniquement le fichier local
    Utile en notebook pour ne pas dépendre du backend au moment de l'EDA.
    """
    if prefer_api:
        try:
            return fetch_mesures_from_api(limit=api_limit)
        except (ConnectionError, RuntimeError) as e:
            print(f"⚠️  API indisponible : {e}")
            if fake_path:
                print(f"↩️  Fallback sur fichier local : {fake_path}")
                return load_from_file(fake_path)
            raise
 
    if fake_path:
        return load_from_file(fake_path)
 
    raise ValueError("❌ Aucune source de données fournie.")