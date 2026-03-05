import threading 
import time
from config import SENSORS, INTERVALS
from sensors.simulator import TurbineSimulator
from Script.init_db import *
from storage.database import get_db
from storage.models import Reading

# Inicialización DB: 
init_db()

def run_sensor(sensor, simulator):
    """
    Función para multithreading. 

    Contiene:
        - Lectura
        - Almacenamiento en DB
        - LOGS (para debug) -> Eliminar en Producción
        - Espera del intervalo del sensor    
    """
    while True:
        # Generamos lectura con simulador
        reading = simulator.generate_reading(sensor)
        """
        Nota Personal: usamos una variable generator
        para centralizar un único simulador para todos los
        sensores. 

        De esta manera el sensor de temperatura, vibración y potencia
        tendrían el mismo estado compartido y pueden correlacionarse. 

        De lo contrario (sin la variable) tendríamos estados distintos
        para cada uno de los sensores (lo cual no es realista)        
        """

        # Administramos Sesión y Guardamos en MySQL
        db = next(get_db())
        try: 
            db_reading = Reading(
                sensor_id   = reading["sensor_id"],
                sensor_type = reading["sensor_type"],
                value       = reading["value"],
                unit        = reading["unit"],
                notes       = reading["notes"],
                timestamp   = reading["timestamp"]
                )
            db.add(db_reading)
            db.commit()
        except Exception as e: 
            db.rollback()   # Revertimos cambios
            print (f"Error en Guardado: {e}")
        finally: 
            db.close()

        # Descomentar si lo veo necesario
        print(f"[{reading['timestamp']}] - {reading['sensor_id']}: {reading['value']} {reading['unit']} | Estado: {simulator.state}")

        time.sleep(INTERVALS[sensor["type"]])