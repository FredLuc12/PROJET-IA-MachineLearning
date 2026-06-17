"""
ml/src/data/cleaner.py
----------------------
Nettoyage et validation des données brutes.
Gère les valeurs manquantes, les outliers, et les doublons.
"""
 
import pandas as pd
import numpy as np
 
 
# ── Plages physiquement valides ────────────────────────────────────────────────
 
VALID_RANGES = {
    "humidite_sol": (0.0, 100.0),
    "temperature":  (-10.0, 60.0),
    "humidite_air": (0.0, 100.0),
}
 
 
def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Supprime les doublons sur (id_capteur, timestamp)."""
    before = len(df)
    df = df.drop_duplicates(subset=["id_capteur", "timestamp"])
    after = len(df)
    if before != after:
        print(f"🧹 Doublons supprimés : {before - after}")
    return df
 
 
def drop_missing_core(df: pd.DataFrame) -> pd.DataFrame:
    """Supprime les lignes sans valeur sur les 3 features clés."""
    core_cols = ["humidite_sol", "temperature", "humidite_air"]
    before = len(df)
    df = df.dropna(subset=core_cols)
    after = len(df)
    if before != after:
        print(f"🧹 Lignes incomplètes supprimées : {before - after}")
    return df
 
 
def clip_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remplace les valeurs hors plage physique par les bornes min/max.
    Ex: humidité sol à 105% → clampée à 100%.
    """
    for col, (low, high) in VALID_RANGES.items():
        if col in df.columns:
            n_outliers = ((df[col] < low) | (df[col] > high)).sum()
            if n_outliers > 0:
                print(f"⚠️  {n_outliers} outliers sur '{col}' → clampés à [{low}, {high}]")
            df[col] = df[col].clip(lower=low, upper=high)
    return df
 
 
def fill_missing_interpolate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Interpolation linéaire sur les valeurs manquantes résiduelles.
    S'assure que le DataFrame est trié par timestamp avant.
    """
    df = df.sort_values("timestamp").reset_index(drop=True)
    numeric_cols = ["humidite_sol", "temperature", "humidite_air"]
    for col in numeric_cols:
        n_missing = df[col].isna().sum()
        if n_missing > 0:
            df[col] = df[col].interpolate(method="linear", limit_direction="both")
            print(f"🔧 {n_missing} valeurs manquantes interpolées sur '{col}'")
    return df
 
 
def clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pipeline complet de nettoyage.
    À appeler après load, avant feature_builder.
    """
    print("── Nettoyage des données ──────────────────────")
    df = remove_duplicates(df)
    df = drop_missing_core(df)
    df = clip_outliers(df)
    df = fill_missing_interpolate(df)
    print(f"✅ Dataset propre : {len(df)} lignes\n")
    return df