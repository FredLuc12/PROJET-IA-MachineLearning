"""
backend/app/db/session.py
----------------------------
Connexion SQLAlchemy à PostgreSQL.
Équivalent du api/database.py de Said, adapté à la structure cible
(config centralisée via core/config.py au lieu de constantes en dur).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base  # noqa: F401  (réexport pour Alembic)

engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency FastAPI : fournit une session DB et la ferme proprement."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
