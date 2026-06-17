"""
ml/src/models/train_classifier.py
----------------------------------
Entraîne un RandomForestClassifier pour classifier l'état du sol :
    sec / normal / humide
 
Sauvegarde :
    ml/models/classifier.joblib
    ml/models/scaler.joblib
    ml/reports/metrics/classifier_report.json
"""
 
import json
from pathlib import Path
 
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.preprocessing import LabelEncoder, StandardScaler
 
from ml.src.data.feature_builder import get_feature_columns
from ml.src.data.splitter import temporal_split, prepare_Xy
 
# ── Chemins de sortie ──────────────────────────────────────────────────────────
MODELS_DIR  = Path("ml/models")
REPORTS_DIR = Path("ml/reports/metrics")
MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 
 
def train_classifier(df: pd.DataFrame) -> dict:
    """
    Entraîne et évalue le classifieur d'état du sol.
 
    Args:
        df : DataFrame avec features et label 'etat_sol'
 
    Returns:
        dict avec les métriques d'évaluation
    """
    cols = get_feature_columns()
    feature_cols = cols["features"]
    label_col    = cols["label_classification"]
 
    # ── Split temporel ─────────────────────────────────────────────────────────
    train_df, test_df = temporal_split(df)
 
    # ── Encodage classes : humide=0, normal=1, sec=2 (ordre alphabétique) ──────
    le = LabelEncoder()
 
    X_train, y_train, scaler, le = prepare_Xy(
        train_df, feature_cols, label_col,
        label_encoder=le, fit=True
    )
    X_test, y_test, _, _ = prepare_Xy(
        test_df, feature_cols, label_col,
        scaler=scaler, label_encoder=le, fit=False
    )
 
    # ── Modèle ─────────────────────────────────────────────────────────────────
    print("🌲 Entraînement RandomForestClassifier...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_leaf=5,
        class_weight="balanced",   # gère le déséquilibre des classes
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
 
    # ── Évaluation ─────────────────────────────────────────────────────────────
    y_pred = model.predict(X_test)
    acc    = accuracy_score(y_test, y_pred)
    report = classification_report(
        y_test, y_pred,
        target_names=le.classes_,
        output_dict=True
    )
    cm = confusion_matrix(y_test, y_pred).tolist()
 
    # Feature importance
    importances = dict(zip(feature_cols, model.feature_importances_.round(4).tolist()))
 
    metrics = {
        "model":            "RandomForestClassifier",
        "accuracy":         round(acc, 4),
        "classes":          le.classes_.tolist(),
        "classification_report": report,
        "confusion_matrix": cm,
        "feature_importances": importances,
        "train_size":       len(train_df),
        "test_size":        len(test_df),
    }
 
    print(f"✅ Accuracy : {acc:.4f}")
    print(f"   Classes  : {le.classes_.tolist()}")
 
    # ── Sauvegarde ─────────────────────────────────────────────────────────────
    joblib.dump(model,  MODELS_DIR / "classifier.joblib")
    joblib.dump(scaler, MODELS_DIR / "scaler.joblib")
    joblib.dump(le,     MODELS_DIR / "label_encoder.joblib")
 
    with open(REPORTS_DIR / "classifier_report.json", "w") as f:
        json.dump(metrics, f, indent=2)
 
    print(f"💾 Modèle sauvegardé → {MODELS_DIR}/classifier.joblib")
    return metrics
 
 
if __name__ == "__main__":
    from ml.src.data.loader import load_combined
    from ml.src.data.cleaner import clean
    from ml.src.data.feature_builder import build_features
 
    df = load_combined(fake_path="data/raw/fake_mesures.json", prefer_api=False)
    df = clean(df)
    df = build_features(df)
    metrics = train_classifier(df)
    print(json.dumps(metrics, indent=2))