"""
ml/src/data/splitter.py
------------------------
Séparation train/test temporelle.
On ne mélange PAS aléatoirement pour respecter l'ordre chronologique
(évite le data leakage sur des séries temporelles).
"""
 
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
 
 
def temporal_split(
    df: pd.DataFrame,
    test_ratio: float = 0.2,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Coupe le DataFrame chronologiquement :
    - 80% → train (données passées)
    - 20% → test  (données récentes)
    """
    n = len(df)
    split_idx = int(n * (1 - test_ratio))
    train = df.iloc[:split_idx].copy()
    test  = df.iloc[split_idx:].copy()
    print(f"📊 Split : train={len(train)} | test={len(test)}")
    return train, test
 
 
def prepare_Xy(
    df: pd.DataFrame,
    feature_cols: list[str],
    label_col: str,
    scaler: StandardScaler | None = None,
    label_encoder: LabelEncoder | None = None,
    fit: bool = True,
) -> tuple:
    """
    Prépare X (features normalisées) et y (label encodé si classification).
 
    Args:
        df            : DataFrame avec features et label
        feature_cols  : colonnes features
        label_col     : colonne cible
        scaler        : StandardScaler (None = créer un nouveau)
        label_encoder : LabelEncoder pour labels texte (None si numérique/bool)
        fit           : True sur train, False sur test
 
    Returns:
        X, y, scaler, label_encoder (ou None si pas de label encoder)
    """
    X = df[feature_cols].values
 
    # Normalisation
    if scaler is None:
        scaler = StandardScaler()
    if fit:
        X = scaler.fit_transform(X)
    else:
        X = scaler.transform(X)
 
    y_raw = df[label_col].values
 
    # Encodage label si texte (ex: "sec" / "normal" / "humide")
    if label_encoder is not None or (
        hasattr(y_raw[0], "__len__") or isinstance(y_raw[0], str)
    ):
        if label_encoder is None:
            label_encoder = LabelEncoder()
        if fit:
            y = label_encoder.fit_transform(y_raw)
        else:
            y = label_encoder.transform(y_raw)
    else:
        y = y_raw.astype(float)
        label_encoder = None
 
    return X, y, scaler, label_encoder