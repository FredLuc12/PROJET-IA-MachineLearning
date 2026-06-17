from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from models import Mesure, Parcelle, Capteur, Irrigation, RecommandationML
from schemas import MesureCreate, MesureOut, ParcelleCreate, ParcelleOut, CapteurOut, RecommandationOut

app = FastAPI(
    title="HydroSmart API",
    description="Système d'irrigation intelligente — H3 Hitema M2 IoT",
    version="1.0.0",
)

@app.get("/")
def root():
    return {"projet": "HydroSmart", "status": "ok", "version": "1.0.0"}

@app.post("/mesures", response_model=MesureOut, status_code=201)
def create_mesure(payload: MesureCreate, db: Session = Depends(get_db)):
    capteur = db.query(Capteur).filter(Capteur.id_capteur == payload.id_capteur).first()
    if not capteur:
        raise HTTPException(status_code=404, detail=f"Capteur {payload.id_capteur} introuvable")
    mesure = Mesure(
        id_capteur=payload.id_capteur,
        humidite_sol=payload.humidite_sol,
        temperature=payload.temperature,
        humidite_air=payload.humidite_air,
        timestamp=datetime.now(),
    )
    db.add(mesure)
    db.commit()
    db.refresh(mesure)
    if payload.humidite_sol < 30.0:
        irrigation = Irrigation(
            id_parcelle=capteur.id_parcelle,
            date_debut=datetime.now(),
            volume_eau=0.0,
            mode="automatique",
        )
        db.add(irrigation)
        db.commit()
    return mesure

@app.get("/mesures", response_model=List[MesureOut])
def get_mesures(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Mesure).order_by(Mesure.timestamp.desc()).limit(limit).all()

@app.get("/mesures/{id_mesure}", response_model=MesureOut)
def get_mesure(id_mesure: int, db: Session = Depends(get_db)):
    mesure = db.query(Mesure).filter(Mesure.id_mesure == id_mesure).first()
    if not mesure:
        raise HTTPException(status_code=404, detail="Mesure introuvable")
    return mesure

@app.get("/parcelles", response_model=List[ParcelleOut])
def get_parcelles(db: Session = Depends(get_db)):
    return db.query(Parcelle).all()

@app.post("/parcelles", response_model=ParcelleOut, status_code=201)
def create_parcelle(payload: ParcelleCreate, db: Session = Depends(get_db)):
    parcelle = Parcelle(**payload.model_dump())
    db.add(parcelle)
    db.commit()
    db.refresh(parcelle)
    return parcelle

@app.get("/capteurs", response_model=List[CapteurOut])
def get_capteurs(db: Session = Depends(get_db)):
    return db.query(Capteur).all()

@app.get("/irrigations")
def get_irrigations(db: Session = Depends(get_db)):
    return db.query(Irrigation).order_by(Irrigation.date_debut.desc()).limit(20).all()

@app.get("/recommandations", response_model=List[RecommandationOut])
def get_recommandations(db: Session = Depends(get_db)):
    return db.query(RecommandationML).order_by(RecommandationML.timestamp.desc()).limit(20).all()

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    derniere = db.query(Mesure).order_by(Mesure.timestamp.desc()).first()
    return {
        "total_mesures": db.query(Mesure).count(),
        "total_irrigations": db.query(Irrigation).count(),
        "total_recos_ml": db.query(RecommandationML).count(),
        "derniere_mesure": {
            "temperature": derniere.temperature if derniere else None,
            "humidite_sol": derniere.humidite_sol if derniere else None,
            "humidite_air": derniere.humidite_air if derniere else None,
            "timestamp": str(derniere.timestamp) if derniere else None,
        }
    }