from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone, timedelta
from typing import Optional
from storage.database import get_db
from storage.models import Reading, Anomaly
from api.schemas import ReadingSchema, AnomalySchema, TurbineStatusSchema, AnomalyStatsSchema


router = APIRouter()


# ========================================
# LECTURAS 
# ========================================
# Genérico
@router.get("/readings", response_model=list[ReadingSchema])
async def get_readings(db: Session = Depends(get_db)):  # Conectamos a la base de datos
    return db.query(Reading).order_by(Reading.timestamp.desc()).limit(100).all()

# Para cada sensor
@router.get("/readings/{sensor_id}", response_model=list[ReadingSchema])
async def sensor_reading(sensor_id : str, db: Session = Depends(get_db)):
    return db.query(Reading).filter(Reading.sensor_id == sensor_id).order_by(Reading.timestamp.desc()).limit(100).all()

# =========================================
# ANOMALÍAS
# =========================================
@router.get("/anomalies", response_model=list[AnomalySchema])
async def get_anomalies(db: Session = Depends(get_db)):
    """Devuelve anomalías registradas"""
    return db.query(Anomaly).all()

@router.get("/anomalies/stats", response_model=list[AnomalyStatsSchema])
async def get_anomaly_stats(db: Session = Depends(get_db)):
    """Devuelve el conteo de anomalías agrupado por tipo"""
    results = (
        db.query(Anomaly.anom_type, func.count(Anomaly.id).label("total"))
        .group_by(Anomaly.anom_type)
        .all()
    )
    return [{"anom_type": r.anom_type, "total": r.total} for r in results]

# =======================================
# ESTADO del SISTEMA
# ======================================
@router.get("/status", response_model=TurbineStatusSchema)
async def get_turbine_status(db: Session = Depends(get_db)):
    """
    Devuelve el estado actual del sistema:
    última lectura por sensor e incidentes en la última hora
    """
    sensors = ["temp_turbine_01", "pow_turbine_01", "vib_turbine_01"]
    last_readings = {}
 
    for sensor_id in sensors:
        last = (
            db.query(Reading)
            .filter(Reading.sensor_id == sensor_id)
            .order_by(Reading.timestamp.desc())
            .first()
        )
        if last:
            last_readings[sensor_id] = {
                "value": last.value,
                "unit": last.unit,
                "timestamp": last.timestamp,
            }
 
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    incidents_last_hour = (
        db.query(func.count(Anomaly.id))
        .join(Reading, Anomaly.owner_id == Reading.id)
        .filter(Reading.timestamp >= one_hour_ago)
        .scalar()
    )
 
    return {
        "last_readings": last_readings,
        "incidents_last_hour": incidents_last_hour,
    }