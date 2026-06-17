"""
ml/src/utils/plotting.py
-------------------------
Fonctions de visualisation réutilisables (matplotlib / seaborn).
Toutes les fonctions sauvegardent optionnellement la figure.
"""
 
from pathlib import Path
from typing import Optional
 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import ConfusionMatrixDisplay
 
FIGURES_DIR = Path("ml/reports/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
 
sns.set_theme(style="darkgrid", palette="muted")
 
COLORS = {
    "sol":    "#4e79a7",
    "temp":   "#f28e2b",
    "air":    "#76b7b2",
    "pred":   "#e15759",
    "sec":    "#e15759",
    "normal": "#59a14f",
    "humide": "#4e79a7",
}
 
 
# ── Séries temporelles ─────────────────────────────────────────────────────────
 
def plot_time_series(
    df: pd.DataFrame,
    save_as: Optional[str] = None,
):
    """Évolution temporelle des 3 features sur la durée complète du dataset."""
    fig, axes = plt.subplots(3, 1, figsize=(16, 10), sharex=True)
 
    axes[0].plot(df["timestamp"], df["humidite_sol"], color=COLORS["sol"], lw=1)
    axes[0].axhline(20, color="red", linestyle="--", alpha=0.6, label="Seuil sec (20%)")
    axes[0].axhline(50, color="orange", linestyle="--", alpha=0.6, label="Seuil normal (50%)")
    axes[0].set_ylabel("Humidité Sol (%)")
    axes[0].set_title("Humidité du Sol", fontweight="bold")
    axes[0].legend(loc="upper right", fontsize=9)
 
    axes[1].plot(df["timestamp"], df["temperature"], color=COLORS["temp"], lw=1)
    axes[1].set_ylabel("Température (°C)")
    axes[1].set_title("Température", fontweight="bold")
 
    axes[2].plot(df["timestamp"], df["humidite_air"], color=COLORS["air"], lw=1)
    axes[2].set_ylabel("Humidité Air (%)")
    axes[2].set_title("Humidité de l'Air", fontweight="bold")
    axes[2].xaxis.set_major_formatter(mdates.DateFormatter("%d/%m %Hh"))
    plt.setp(axes[2].xaxis.get_majorticklabels(), rotation=30)
 
    plt.suptitle("Évolution temporelle — Capteurs ESP32", fontsize=14, fontweight="bold")
    plt.tight_layout()
    _save(save_as)
    plt.show()
 
 
def plot_predictions_vs_actual(
    timestamps: pd.Series,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    title: str = "Prédictions vs Réalité",
    ylabel: str = "Humidité Sol (%)",
    save_as: Optional[str] = None,
):
    """Courbe prédictions régresseur vs valeurs réelles."""
    plt.figure(figsize=(14, 5))
    plt.plot(timestamps, y_true, label="Réel",    color=COLORS["sol"], lw=1.5)
    plt.plot(timestamps, y_pred, label="Prédit",  color=COLORS["pred"], lw=1.5, linestyle="--")
    plt.fill_between(timestamps, y_true, y_pred, alpha=0.12, color="gray")
    plt.xlabel("Timestamp")
    plt.ylabel(ylabel)
    plt.title(title, fontweight="bold")
    plt.legend()
    plt.xticks(rotation=30)
    plt.tight_layout()
    _save(save_as)
    plt.show()
 
 
# ── Classification ─────────────────────────────────────────────────────────────
 
def plot_confusion_matrix(
    cm: list | np.ndarray,
    class_names: list[str],
    save_as: Optional[str] = None,
):
    """Matrice de confusion annotée."""
    cm = np.array(cm)
    fig, ax = plt.subplots(figsize=(6, 5))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
    disp.plot(ax=ax, colorbar=False, cmap="Blues")
    ax.set_title("Matrice de Confusion — État du Sol", fontweight="bold")
    plt.tight_layout()
    _save(save_as)
    plt.show()
 
 
def plot_class_distribution(
    series: pd.Series,
    save_as: Optional[str] = None,
):
    """Barres + pie de la distribution des classes."""
    counts = series.value_counts()
    colors = [COLORS.get(c, "#aaa") for c in counts.index]
 
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
 
    bars = axes[0].bar(counts.index, counts.values, color=colors, edgecolor="white")
    for bar, val in zip(bars, counts.values):
        axes[0].text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 5,
            str(val), ha="center", fontweight="bold", fontsize=10,
        )
    axes[0].set_title("Nombre de mesures par état", fontweight="bold")
    axes[0].set_ylabel("Mesures")
 
    axes[1].pie(
        counts.values, labels=counts.index, colors=colors,
        autopct="%1.1f%%", startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
    )
    axes[1].set_title("Répartition des états", fontweight="bold")
 
    plt.suptitle("Distribution — État du Sol", fontsize=13, fontweight="bold")
    plt.tight_layout()
    _save(save_as)
    plt.show()
 
 
# ── Feature importance ─────────────────────────────────────────────────────────
 
def plot_feature_importance(
    importances: dict,
    title: str = "Feature Importance",
    save_as: Optional[str] = None,
):
    """Barres horizontales triées par importance."""
    fi = pd.Series(importances).sort_values(ascending=True)
    plt.figure(figsize=(10, max(4, len(fi) * 0.4)))
    plt.barh(fi.index, fi.values, color=COLORS["sol"], edgecolor="white")
    plt.xlabel("Importance")
    plt.title(title, fontweight="bold")
    plt.tight_layout()
    _save(save_as)
    plt.show()
 
 
# ── Corrélation ────────────────────────────────────────────────────────────────
 
def plot_correlation(
    df: pd.DataFrame,
    cols: list[str] = ["humidite_sol", "temperature", "humidite_air"],
    save_as: Optional[str] = None,
):
    """Heatmap de corrélation."""
    corr = df[cols].corr()
    plt.figure(figsize=(6, 5))
    sns.heatmap(
        corr, annot=True, fmt=".2f", cmap="coolwarm",
        center=0, linewidths=0.5, square=True,
        annot_kws={"size": 13},
    )
    plt.title("Corrélation entre features", fontweight="bold")
    plt.tight_layout()
    _save(save_as)
    plt.show()
 
 
# ── Helpers ────────────────────────────────────────────────────────────────────
 
def _save(filename: Optional[str]):
    if filename:
        path = FIGURES_DIR / filename
        plt.savefig(path, bbox_inches="tight", dpi=120)
        print(f"💾 Figure sauvegardée → {path}")