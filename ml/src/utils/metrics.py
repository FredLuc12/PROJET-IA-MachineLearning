"""
ml/src/utils/metrics.py
------------------------
Fonctions de métriques réutilisables pour classification et régression.
"""
 
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    f1_score,
)
 
 
# ── Classification ─────────────────────────────────────────────────────────────
 
def classification_metrics(y_true, y_pred, class_names: list[str] | None = None) -> dict:
    """Retourne un dict complet de métriques de classification."""
    return {
        "accuracy":   round(accuracy_score(y_true, y_pred), 4),
        "f1_macro":   round(f1_score(y_true, y_pred, average="macro"), 4),
        "f1_weighted":round(f1_score(y_true, y_pred, average="weighted"), 4),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "report": classification_report(
            y_true, y_pred,
            target_names=class_names,
            output_dict=True,
            zero_division=0,
        ),
    }
 
 
# ── Régression ─────────────────────────────────────────────────────────────────
 
def regression_metrics(y_true, y_pred) -> dict:
    """Retourne un dict complet de métriques de régression."""
    mae  = mean_absolute_error(y_true, y_pred)
    rmse = mean_squared_error(y_true, y_pred) ** 0.5
    r2   = r2_score(y_true, y_pred)
    mape = float(np.mean(np.abs((y_true - y_pred) / (np.abs(y_true) + 1e-8))) * 100)
 
    return {
        "mae":  round(mae,  4),
        "rmse": round(rmse, 4),
        "r2":   round(r2,   4),
        "mape": round(mape, 4),
    }
 
 
def print_regression_metrics(metrics: dict, label: str = "Régression"):
    print(f"── {label} ──────────────────────────────")
    print(f"   MAE  : {metrics['mae']:.3f}%")
    print(f"   RMSE : {metrics['rmse']:.3f}%")
    print(f"   R²   : {metrics['r2']:.4f}")
    print(f"   MAPE : {metrics['mape']:.2f}%")
 
 
def print_classification_metrics(metrics: dict, label: str = "Classification"):
    print(f"── {label} ──────────────────────────────")
    print(f"   Accuracy    : {metrics['accuracy']:.4f}")
    print(f"   F1 macro    : {metrics['f1_macro']:.4f}")
    print(f"   F1 weighted : {metrics['f1_weighted']:.4f}")