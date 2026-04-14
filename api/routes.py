from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone, timedelta
from typing import Optional
from storage.database import get_db, engine
import pandas as pd
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
        "incidents_last_hour": incidents_last_hour,
    }

# ======================================
# ANALÍTICA
# ======================================
@router.get("/analytics/summary")
async def get_analytics_summary():
    """
    Extrae los últimos datos de la base de datos
    a un dataframe de Pandas para posterior análisis de correlación
    
    Valores entre: 
    1: Suben juntos
    0: No relación
    -1: Uno sube otro baja
    """
    # Extraemos los datos usando Pandas SQL directamente
    query = "SELECT * FROM reading ORDER BY timestamp DESC LIMIT 3000"
    df = pd.read_sql(query, engine)

    if df.empty:
        return {"status": "error", "message": "Faltan lecturas para el análisis."}

    stats = df.groupby("sensor_type")["value"].agg(["mean", "max", "min", "std"])
    stats = stats.fillna(0).to_dict(orient="index")

    # Preparación de datos para Correlación
    # Pivotamos la tabla (las filas son timestamps, las columnas los tipos de sensor)
    pivot_df = df.pivot_table(index='timestamp', columns='sensor_type', values='value', aggfunc='mean')
    
    #Rellenamos los huecos por si algún sensor se leyó unos milisegundos más tarde (ffill)
    pivot_df = pivot_df.ffill().bfill()
    
    # Matriz de Correlación: ver si cuando X sube, Y sube
    corr_matrix = pivot_df.corr().fillna(0).to_dict()

    return {
        "status": "success",
        "data_points_analyzed": len(df),
        "statistics_by_sensor": stats,
        "correlation_matrix": corr_matrix,
        "business_value": "Visualización matricial de correlaciones y estadísticas de planta"
    }

@router.get("/analytics/export")
async def export_analytics(window: int = Query(5, description="Ventana para Media Móvil")):
    """
    Exporta datos en formato CSV aplicando una media móvil
    para suavizar el ruido temporal
    """
    query = "SELECT * FROM reading ORDER BY timestamp DESC LIMIT 5000"
    df = pd.read_sql(query, engine)

    if df.empty:
        return {"status": "error", "message": "Faltan lecturas para exportar."}

    # Ordenamos por tiempo
    df = df.sort_values(by="timestamp")

    # Usamos GroupBy para no mezclar medias de temperatura con vibración
    df['value_smoothed'] = df.groupby('sensor_id')['value'].transform(lambda x: x.rolling(window=window, min_periods=1).mean())

    # Formateamos CSV
    csv_data = df.to_csv(index=False)
    
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=argus_data.csv"}
    )