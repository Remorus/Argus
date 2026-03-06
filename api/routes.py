from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from storage.database import get_db
from storage.models import Reading, Anomaly
from api.schemas import ReadingSchema, AnomalySchema


router = APIRouter()

# En general
@router.get("/readings", response_model=list[ReadingSchema])
async def get_readings(db: Session = Depends(get_db)):  # Conectamos a la base de datos
    return db.query(Reading).order_by(Reading.timestamp.desc()).limit(100).all()

# Para cada sensor
@router.get("/readings/{sensor_id}", response_model=list[ReadingSchema])
async def sensor_reading(sensor_id : str, db: Session = Depends(get_db)):
    return db.query(Reading).filter(Reading.sensor_id == sensor_id).order_by(Reading.timestamp.desc()).limit(100).all()


# Anomalías
@router.get("/anomalies", response_model=list[AnomalySchema])
async def get_anomalies(db: Session = Depends(get_db)):
    return db.query(Anomaly).all()