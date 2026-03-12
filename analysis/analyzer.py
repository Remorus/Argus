from config import THRESHOLDS
import numpy as np

# Número mínimo de lecturas para análsis estadístico
MIN_HISTORY = 5

def analyze_reading(reading: dict, history:dict) -> str | None:
    """
    Analiza una lectura y devuelve el tipo de anomalía o None
    """
    
    sensor_type = reading["sensor_type"]
    value = reading["value"]
    sensor_id = reading["sensor_id"]

    min_val = THRESHOLDS[sensor_type]["min"]
    max_val = THRESHOLDS[sensor_type]["max"]

    # Si el valor está dentro del rango opracional no hay anomalía
    if min_val <= value <=max_val:
        return None
    
    last_N = history.get(sensor_id,[])

    if value < min_val or value > max_val:

        last_N = history[sensor_id]

    # Si no hay historial suficiente solo podemos marcar out_of_range
    if len(last_N)<MIN_HISTORY:
        return "out_of_range"
    
    values_array = np.array(last_N)

    #DRIFT: todos los valores del historial están fuera del rango
    if all(v<min_val or v>max_val for v in last_N):
        return "drift"
    
    # SPIKE: detección estadística por z-score
    # Si el valor actual se aleja más de 3 desviaciones típicas de la media histórica
    mean = np.mean(values_array)
    std = np.std(values_array)

    if std > 0: 
        z_score = abs(value-mean) / std
        if z_score > 3: 
            return "spike"
    
    # OUT OF RANGE: fuera de umbrales pero sin patrón estadístico claro
    return "out_of_range"
    
    
    
    return None
    