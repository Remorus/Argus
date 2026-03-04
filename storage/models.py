"""
Define la estructura de nuestra base de datos.

Utilizamos SQLAlchemy (ORM) para representar las tablas como clases de Python
Cada clase corresponde a una tabla y sus atributos a las columnas

SQLAlchemy se encarga de traducir automáticamente estas clases a sentencias SQL.
"""

from sqlalchemy import  Column, ForeignKey, Integer, String, DateTime, Float  
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func         # PERMITE USAR FUNCIONES DE SQL típicas 
from database import Base


class Reading(Base):
    __tablename__ = "reading"
    id = Column(Integer, primary_key= True, index= True)    # Aceleramos búsqueda para la columna con index = True 
    sensor_id = Column(String(50),index= True)
    sensor_type = Column(String(50),index= True)
    value = Column(Float,index= True )
    unit = Column(String(20), index= True)
    notes = Column(String(100), nullable=True)      # Nos permitirá guardar la notificación de fallo resuelto
    timestamp = Column(DateTime(timezone=True), server_default=func.now())     

    # Relación con la Tabla de Anomalias
    anomaly = relationship("Anomaly", back_populates="owner") # Relación bidireccional entre tablas (1:n)



class Anomaly(Base):
    __tablename__ = "anomaly"
    id = Column(Integer, primary_key= True, index= True)
    anom_type = Column(String(50),index= True)
    owner_id = Column(Integer, ForeignKey("reading.id"))

    # Relación con la tabla Turbina
    owner = relationship("Reading", back_populates="anomaly") # Bidireccional con relación (1:1)