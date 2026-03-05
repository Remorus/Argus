import threading 
import time
from config import SENSORS, INTERVALS
from sensors.simulator import TurbineSimulator
from script.init_db import init_db
from storage.database import get_db
from storage.models import Reading, Anomaly
from analysis.analyzer import analyze_reading



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


            # Agregamos Análisis de Anomalías: 
            anomaly_type = analyze_reading(reading, simulator.history)

            if anomaly_type:
                db_anomaly = Anomaly(
                    anom_type = anomaly_type,
                    owner_id = db_reading.id
                )
            
                db.add(db_anomaly)
                db.commit()
                print(f" ANOMALÍA: {anomaly_type} en {reading['sensor_id']} valor={reading['value']}")

        except Exception as e: 
            db.rollback()   # Revertimos cambios
            print (f"Error en Guardado: {e}")
        finally: 
            db.close()

        # Descomentar si lo veo necesario
        print(f"[{reading['timestamp']}] - {reading['sensor_id']}: {reading['value']} {reading['unit']} | Estado: {simulator.state}")

        time.sleep(INTERVALS[sensor["type"]])




# Lanzamos los hilos
simulator = TurbineSimulator() # Una sola instancia del simulador (explicado antes)

for s in SENSORS: 
    t = threading.Thread(target=run_sensor, args=(s, simulator), daemon=True)  
    t.start()

# Vamos a mantener el programa vivo hasta CTRL + C ( para no romperlo con daemon = True )
try: 
    while True: 
        time.sleep(1)
except KeyboardInterrupt: 
    print("Sistema detenido...")