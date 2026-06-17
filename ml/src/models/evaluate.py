"""
ml/src/models/evaluate.py
--------------------------
Évaluation complète des deux modèles entraînés.
Génère métriques JSON + figures dans ml/reports/.
 
Usage :
    python -m ml.src.models.evaluate
    python -m ml.src.models.evaluate --source file --path data/raw/fake_mesures.json
"""
 
import argparse
import json
from pathlib import Path
 
import joblib
import numpy as np
import pandas as pd
 
from ml.src.data.feature_builder import build_features, get_feature_columns
from ml.src.data.splitter import temporal_split, prepare_Xy
from ml.src.utils.metrics import (
    classification_metrics,
    regression_metrics,
    print_classification_metrics,
    print_regression_metrics,
)
from ml.src.utils.plotting import (
    plot_confusion_matrix,
    plot_feature_importance,
    plot_predictions_vs_actual,
    plot_class_distribution,
)
 
MODELS_DIR  = Path("ml/models")
REPORTS_DIR = Path("ml/reports/metrics")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
 
 
def evaluate(df: pd.DataFrame) -> dict:
    """
    Évalue classifier et regressor sur le split test du DataFrame.
 
    Returns:
        dict avec toutes les métriques
    """
    cols         = get_feature_columns()
    feature_cols = cols["features"]
 
    # ── Chargement modèles ────────────────────────────────────────────────────
    clf        = joblib.load(MODELS_DIR / "classifier.joblib")
    reg        = joblib.load(MODELS_DIR / "regressor.joblib")
    scaler     = joblib.load(MODELS_DIR / "scaler.joblib")
    le         = joblib.load(MODELS_DIR / "label_encoder.joblib")
    scaler_reg = joblib.load(MODELS_DIR / "scaler_reg.joblib")
 
    # ── Split test (20% dernières données) ────────────────────────────────────
    _, test_df = temporal_split(df, test_ratio=0.2)
 
    # ── Évaluation Classifieur ────────────────────────────────────────────────
    print("\n📊 Évaluation — Classifieur\n")
    X_test_clf, y_test_clf, _, _ = prepare_Xy(
        test_df, feature_cols, cols["label_classification"],
        scaler=scaler, label_encoder=le, fit=False,
    )
    y_pred_clf = clf.predict(X_test_clf)
 
    clf_metrics = classification_metrics(
        y_test_clf, y_pred_clf,
        class_names=le.classes_.tolist(),
    )
    print_classification_metrics(clf_metrics)
 
    # Figures classifieur
    plot_confusion_matrix(
        clf_metrics["confusion_matrix"],
        class_names=le.classes_.tolist(),
        save_as="eval_confusion_matrix.png",
    )
    fi_clf = dict(zip(feature_cols, clf.feature_importances_.round(4).tolist()))
    plot_feature_importance(fi_clf, title="Feature Importance — Classifieur",
                            save_as="eval_feature_importance_clf.png")
 
    # Distribution classes sur le test set
    y_pred_labels = le.inverse_transform(y_pred_clf)
    plot_class_distribution(
        pd.Series(y_pred_labels, name="etat_sol"),
        save_as="eval_class_distribution_pred.png",
    )
 
    # ── Évaluation Régresseur ──────────────────────────────────────────────────
    print("\n📊 Évaluation — Régresseur\n")
    X_test_reg, y_test_reg, _, _ = prepare_Xy(
        test_df, feature_cols, cols["label_regression"],
        scaler=scaler_reg, label_encoder=None, fit=False,
    )
    y_pred_reg = reg.predict(X_test_reg)
 
    reg_metrics = regression_metrics(y_test_reg, y_pred_reg)
    print_regression_metrics(reg_metrics)
 
    plot_predictions_vs_actual(
        timestamps=test_df["timestamp"].reset_index(drop=True),
        y_true=y_test_reg,
        y_pred=y_pred_reg,
        title="Régresseur — Humidité Sol Prévue vs Réelle",
        save_as="eval_regressor_predictions.png",
    )
 
    fi_reg = dict(zip(feature_cols, reg.feature_importances_.round(4).tolist()))
    plot_feature_importance(fi_reg, title="Feature Importance — Régresseur",
                            save_as="eval_feature_importance_reg.png")
 
    # ── Rapport global ─────────────────────────────────────────────────────────
    report = {
        "test_size":    len(test_df),
        "classifier":   {**clf_metrics, "model": "RandomForestClassifier"},
        "regressor":    {**reg_metrics, "model": "RandomForestRegressor"},
    }
 
    out_path = REPORTS_DIR / "evaluation_report.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n💾 Rapport sauvegardé → {out_path}")
 
    return report
 
 
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["file", "api"], default="file")
    parser.add_argument("--path",   default="data/raw/fake_mesures.json")
    parser.add_argument("--limit",  type=int, default=500)
    args = parser.parse_args()
 
    from ml.src.data.loader import load_combined
    from ml.src.data.cleaner import clean
 
    df = load_combined(
        fake_path=args.path if args.source == "file" else None,
        api_limit=args.limit,
        prefer_api=args.source == "api",
    )
    df = clean(df)
    df = build_features(df)
    evaluate(df)