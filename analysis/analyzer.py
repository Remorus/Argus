from config import THRESHOLDS

def analyze_reading(reading, history):
    """
    Analiza una lectura y devuelve el tipo de anomalía o None
    """
    
    sensor_type = reading["sensor_type"]
    value = reading["value"]
    sensor_id = reading["sensor_id"]

    min_val = THRESHOLDS[sensor_type]["min"]
    max_val = THRESHOLDS[sensor_type]["max"]


    
    if value < min_val or value > max_val:

        last_N = history[sensor_id]

        # DRIFT : Valor a la deriva en varios registros
        if all (l<min_val or l>max_val for l in last_N):
            return "drift"
        
        # SPIKE: Fuera de Rango pero puntual
    
        outrange_count = sum(1 for l in last_N if l<min_val or l>max_val)

        if outrange_count == 1:
            return "spike"

        # OUT OF RANGE: Valor fuera de rango pero sin patrón claro
        return "out_of_range"
    
    
    
    return None
    