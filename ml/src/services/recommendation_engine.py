"""
ml/src/services/recommendation_engine.py
------------------------------------------
Logique métier de décision d'irrigation.
Combine la prédiction ML avec des règles métier (seuils, cooldown, heure).
C'est la couche entre predict.py et l'API POST /recommandations.

Usage :
    from ml.src.services.recommendation_engine import RecommendationEngine

    engine = RecommendationEngine()
    decision = engine.decide({
        "id_mesure":    42,
        "humidite_sol": 14.5,
        "temperature":  31.0,
        "humidite_air": 42.0,
        "timestamp":    "2026-06-16T14:32:05",
    })
"""

import os
from datetime import datetime, timedelta
from typing import Optional

import requests

from ml.src.models.predict import predict_single

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
MODEL_NAME   = "RandomForest"

# ── Règles métier ──────────────────────────────────────────────────────────────
CRITICAL_SOIL_THRESHOLD = 10.0   # % → irrigation forcée, peu importe l'heure
NO_IRRIGATE_HOURS       = (22, 6) # entre 22h et 6h → pas d'irrigation (nuit)
COOLDOWN_MINUTES        = 30     # délai min entre deux irrigations


class RecommendationEngine:
    """
    Moteur de recommandation d'irrigation.
    Combine prédiction ML + règles métier + cooldown.
    """

    def __init__(self):
        self._last_irrigation_time: Optional[datetime] = None

    def decide(self, mesure: dict, dry_run: bool = False) -> dict:
        """
        Prend une décision d'irrigation pour une mesure donnée.

        Args:
            mesure   : dict avec id_mesure, humidite_sol, temperature,
                       humidite_air, timestamp
            dry_run  : si True, ne poste pas à l'API

        Returns:
            {
                "id_mesure":        int,
                "besoin_eau":       bool,
                "humidite_prevue":  float,
                "etat_sol":         str,
                "reason":           str,   ← explication de la décision
                "posted":           bool,  ← True si envoyé à l'API
            }
        """
        ts = datetime.fromisoformat(str(mesure.get("timestamp", datetime.now().isoformat())))
        humidite_sol = float(mesure.get("humidite_sol", 50.0))

        # ── 1. Prédiction ML ──────────────────────────────────────────────────
        prediction = predict_single(mesure)
        besoin_eau = prediction["besoin_eau"]
        etat_sol   = prediction["etat_sol"]
        humidite_prevue = prediction["humidite_prevue"]

        # ── 2. Règles métier ──────────────────────────────────────────────────
        reason = "ML: " + ("irrigation recommandée" if besoin_eau else "sol suffisamment humide")

        # Seuil critique → force l'irrigation
        if humidite_sol < CRITICAL_SOIL_THRESHOLD:
            besoin_eau = True
            reason = f"CRITIQUE: humidité sol à {humidite_sol}% < {CRITICAL_SOIL_THRESHOLD}%"

        # Restriction nocturne
        hour = ts.hour
        night_start, night_end = NO_IRRIGATE_HOURS
        is_night = (hour >= night_start) or (hour < night_end)
        if besoin_eau and is_night and humidite_sol >= CRITICAL_SOIL_THRESHOLD:
            besoin_eau = False
            reason = f"Nuit ({hour}h) — irrigation suspendue (sauf urgence critique)"

        # Cooldown : évite deux irrigations trop rapprochées
        if besoin_eau and self._last_irrigation_time:
            elapsed = (ts - self._last_irrigation_time).total_seconds() / 60
            if elapsed < COOLDOWN_MINUTES:
                besoin_eau = False
                reason = f"Cooldown : dernière irrigation il y a {elapsed:.0f} min (min {COOLDOWN_MINUTES} min)"

        # Mémoriser si on irrigue
        if besoin_eau:
            self._last_irrigation_time = ts

        # ── 3. Post API ───────────────────────────────────────────────────────
        posted = False
        if not dry_run:
            posted = self._post_recommendation(
                id_mesure=int(mesure.get("id_mesure", 0)),
                besoin_eau=besoin_eau,
                humidite_prevue=humidite_prevue,
            )

        return {
            "id_mesure":       mesure.get("id_mesure"),
            "besoin_eau":      besoin_eau,
            "humidite_prevue": humidite_prevue,
            "etat_sol":        etat_sol,
            "reason":          reason,
            "posted":          posted,
        }

    def _post_recommendation(
        self,
        id_mesure: int,
        besoin_eau: bool,
        humidite_prevue: float,
    ) -> bool:
        """Envoie POST /recommandations à l'API de Said."""
        try:
            url    = f"{API_BASE_URL}/recommandations"
            params = {
                "id_mesure":             id_mesure,
                "besoin_eau":            str(besoin_eau).lower(),
                "niveau_humidite_prevu": humidite_prevue,
                "modele_utilise":        MODEL_NAME,
            }
            resp = requests.post(url, params=params, timeout=10)
            resp.raise_for_status()
            return True
        except Exception as e:
            print(f"   ⚠️  Erreur POST recommandation : {e}")
            return False

    def reset_cooldown(self):
        """Réinitialise le cooldown (utile pour les tests)."""
        self._last_irrigation_time = None