"""
ml/src/data/feature_builder.py
--------------------------------
Construction des features ML à partir des données brutes nettoyées.
Gère aussi les labels pour classification et régression.
"""
 
import pandas as pd
import numpy as np
 
# ── Seuils (identiques au générateur de fake data) ────────────────────────────
SOIL_DRY_THRESHOLD    = 20.0
SOIL_NORMAL_THRESHOLD = 50.0
 
 
# ── Features temporelles ───────────────────────────────────────────────────────
 
def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extrait des features cycliques depuis le timestamp."""
    df = df.copy()
    dt = df["timestamp"]
 
    df["hour"]        = dt.dt.hour + dt.dt.minute / 60
    df["day_of_week"] = dt.dt.dayofweek          # 0=Lundi, 6=Dimanche
    df["month"]       = dt.dt.month
 
    # Encodage cyclique (sin/cos) pour que 23h et 0h soient proches
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
 
    return df
 
 
# ── Features glissantes ────────────────────────────────────────────────────────
 
def add_rolling_features(df: pd.DataFrame, windows: list[int] = [3, 6, 12]) -> pd.DataFrame:
    """
    Moyennes mobiles sur humidité sol, temp, humidité air.
    window=3 → moyenne sur 3 mesures précédentes (= 15 min si intervalle 5min)
    """
    df = df.copy()
    for w in windows:
        df[f"humidite_sol_mean_{w}"] = (
            df["humidite_sol"].rolling(window=w, min_periods=1).mean().round(2)
        )
        df[f"temperature_mean_{w}"] = (
            df["temperature"].rolling(window=w, min_periods=1).mean().round(2)
        )
 
    # Tendance : différence entre valeur actuelle et la précédente
    df["humidite_sol_delta"] = df["humidite_sol"].diff().fillna(0).round(2)
 
    return df
 
 
# ── Labels ─────────────────────────────────────────────────────────────────────
 
def add_classification_label(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ajoute le label 'etat_sol' si absent.
    sec / normal / humide selon seuils.
    """
    df = df.copy()
    if df["etat_sol"].isna().all():
        def _label(h):
            if h < SOIL_DRY_THRESHOLD:
                return "sec"
            elif h < SOIL_NORMAL_THRESHOLD:
                return "normal"
            return "humide"
        df["etat_sol"] = df["humidite_sol"].apply(_label)
    return df
 
 
def add_binary_label(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ajoute le label binaire 'besoin_eau' (True/False) si absent.
    True si humidité sol < seuil sec.
    """
    df = df.copy()
    if df["besoin_eau"].isna().all():
        df["besoin_eau"] = df["humidite_sol"] < SOIL_DRY_THRESHOLD
    df["besoin_eau"] = df["besoin_eau"].astype(bool)
    return df
 
 
def add_regression_label(df: pd.DataFrame, horizon: int = 6) -> pd.DataFrame:
    """
    Ajoute le label 'humidite_prevue' : humidité sol dans `horizon` mesures.
    Utilisé pour la régression (prédiction future).
    Si déjà présent (fake data), on ne l'écrase pas.
    """
    df = df.copy()
    if df["humidite_prevue"].isna().all():
        df["humidite_prevue"] = (
            df["humidite_sol"].shift(-horizon).round(1)
        )
    return df
 
 
# ── Pipeline complet ───────────────────────────────────────────────────────────
 
def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pipeline complet de feature engineering.
    À appeler après clean().
    """
    print("── Feature Engineering ────────────────────────")
    df = add_time_features(df)
    df = add_rolling_features(df)
    df = add_classification_label(df)
    df = add_binary_label(df)
    df = add_regression_label(df)
 
    # Supprime les lignes où le label de régression est NaN (dernières lignes)
    before = len(df)
    df = df.dropna(subset=["humidite_prevue"])
    dropped = before - len(df)
    if dropped:
        print(f"   Lignes sans label régression supprimées : {dropped}")
 
    print(f"✅ Features construites : {len(df)} lignes, {df.shape[1]} colonnes\n")
    return df
 
 
def get_feature_columns() -> dict:
    """Retourne les listes de colonnes pour chaque usage ML."""
    return {
        # Features d'entrée communes
        "features": [
            "humidite_sol",
            "temperature",
            "humidite_air",
            "hour_sin",
            "hour_cos",
            "day_of_week",
            "humidite_sol_mean_3",
            "humidite_sol_mean_6",
            "humidite_sol_mean_12",
            "temperature_mean_3",
            "humidite_sol_delta",
        ],
        # Label classification multi-classe
        "label_classification": "etat_sol",
        # Label classification binaire
        "label_binary": "besoin_eau",
        # Label régression
        "label_regression": "humidite_prevue",
    }