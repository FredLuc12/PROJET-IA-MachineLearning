"""
backend/app/main.py
----------------------
Point d'entrée FastAPI.
Toute la logique métier a été déplacée dans services/, repositories/, api/routes/.
Lancement : uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.router import api_router

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)

# CORS pour permettre au frontend Next.js (autre port) d'appeler l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # à restreindre en prod
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
