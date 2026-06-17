"""
backend/app/core/config.py
----------------------------
Configuration centralisée de l'application.
Toutes les valeurs sensibles passent par variables d'environnement (.env).
"""

import os
from functools import lru_cache


class Settings:
    # ── Base de données ────────────────────────────────────────────────────────
    DB_USER:     str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST:     str = os.getenv("DB_HOST", "localhost")
    DB_PORT:     str = os.getenv("DB_PORT", "5432")
    DB_NAME:     str = os.getenv("DB_NAME", "hydrosmart")

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # ── API ────────────────────────────────────────────────────────────────────
    APP_NAME:    str = "HydroSmart API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Système d'irrigation intelligente — H3 Hitema M2 IoT"

    # ── Seuils métier (utilisés aussi par le ML) ─────────────────────────────────
    SOIL_DRY_THRESHOLD: float = float(os.getenv("SOIL_DRY_THRESHOLD", "30.0"))


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
