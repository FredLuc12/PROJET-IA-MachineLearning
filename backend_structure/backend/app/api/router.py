"""
backend/app/api/router.py
----------------------------
Agrège tous les routers de app/api/routes/ en un seul.
Importé une seule fois dans main.py.
"""

from fastapi import APIRouter

from app.api.routes import health, measurements, parcels, sensors, irrigations, recommendations

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(measurements.router)
api_router.include_router(parcels.router)
api_router.include_router(sensors.router)
api_router.include_router(irrigations.router)
api_router.include_router(recommendations.router)
