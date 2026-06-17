"""
backend/app/db/base.py
------------------------
Base déclarative SQLAlchemy, importée par tous les modèles.
Centralisée ici pour éviter les imports circulaires (au lieu de
l'avoir dans database.py comme dans la version de Said).
"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()
