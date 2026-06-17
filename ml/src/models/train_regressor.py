"""
ml/src/models/train_regressor.py
----------------------------------
Entraîne un RandomForestRegressor pour prédire l'humidité sol future.
Horizon : 6 mesures (~30 min si intervalle 5min)
 
Sauvegarde :
    ml/models/regressor.joblib
    ml/reports/metrics/regressor_report.json
"""
 
import json
from pathlib import Path
 
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
 
from ml.src.data.feature_builder import get_feature_columns
from ml.src.data.splitter import temporal_split, prepare_Xy
 
MODELS_DIR  = Path("ml/models")
REPORTS_DIR = Path("ml/reports/metrics")
MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 
 
def train_regressor(df: pd.DataFrame) -> dict:
    """
    Entraîne et évalue le régresseur d'humidité sol prévue.
 
    Args:
        df : DataFrame avec features et label 'humidite_prevue'
 
    Returns:
        dict avec les métriques d'évaluation
    """
    cols = get_feature_columns()
    feature_cols = cols["features"]
    label_col    = cols["label_regression"]
 
    # ── Split temporel ─────────────────────────────────────────────────────────
    train_df, test_df = temporal_split(df)
 
    X_train, y_train, scaler_reg, _ = prepare_Xy(
        train_df, feature_cols, label_col,
        label_encoder=None, fit=True
    )
    X_test, y_test, _, _ = prepare_Xy(
        test_df, feature_cols, label_col,
        scaler=scaler_reg, label_encoder=None, fit=False
    )
 
    # ── Modèle ─────────────────────────────────────────────────────────────────
    print("🌲 Entraînement RandomForestRegressor...")
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=12,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
 
    # ── Évaluation ─────────────────────────────────────────────────────────────
    y_pred = model.predict(X_test)
    mae  = mean_absolute_error(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred) ** 0.5
    r2   = r2_score(y_test, y_pred)
 
    importances = dict(zip(feature_cols, model.feature_importances_.round(4).tolist()))
 
    metrics = {
        "model":               "RandomForestRegressor",
        "mae":                 round(mae, 4),
        "rmse":                round(rmse, 4),
        "r2":                  round(r2, 4),
        "feature_importances": importances,
        "train_size":          len(train_df),
        "test_size":           len(test_df),
    }
 
    print(f"✅ MAE={mae:.3f}%  RMSE={rmse:.3f}%  R²={r2:.4f}")
 
    # ── Sauvegarde ─────────────────────────────────────────────────────────────
    joblib.dump(model,      MODELS_DIR / "regressor.joblib")
    joblib.dump(scaler_reg, MODELS_DIR / "scaler_reg.joblib")
 
    with open(REPORTS_DIR / "regressor_report.json", "w") as f:
        json.dump(metrics, f, indent=2)
 
    print(f"💾 Modèle sauvegardé → {MODELS_DIR}/regressor.joblib")
    return metrics
 
 
if __name__ == "__main__":
    from ml.src.data.loader import load_combined
    from ml.src.data.cleaner import clean
    from ml.src.data.feature_builder import build_features
 
    df = load_combined(fake_path="data/raw/fake_mesures.json", prefer_api=False)
    df = clean(df)
    df = build_features(df)
    metrics = train_regressor(df)
    print(json.dumps(metrics, indent=2))