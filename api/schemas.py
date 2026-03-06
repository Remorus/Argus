from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ReadingSchema (BaseModel):
    id : int = Field(..., description="PrimaryKey")
    sensor_id: str = Field(..., description="Sensor id")
    sensor_type: str = Field(...,description="Sensor Type")
    value : float = Field(..., description="Valor Resitrado")
    unit: str = Field(..., description="Unidad")
    notes : Optional[str] = None
    timestamp : datetime = Field(... , description="Timestamp")
    class Config:
        from_attributes = True         # Esto permite convertir el objeto SQLALchemy a Pydantic


class AnomalySchema (BaseModel):
    id: int = Field(..., description="PrimaryKey")
    anom_type: str = Field(..., description="Tipo de Anomalía")
    owner_id: int = Field(..., description="ForeignKey")
    class Config:
        from_attributes = True         # Esto permite convertir el objeto SQLALchemy a Pydantic
