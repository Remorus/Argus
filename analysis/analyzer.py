from config import THRESHOLDS
import numpy as np

# Número mínimo de lecturas para análsis estadístico
MIN_HISTORY = 5

def analyze_reading(reading: dict, history: dict) -> str | None:
    """
    Analiza una lectura y devuelve el tipo de anomalía o None
    Implementa Mantenimiento Predictivo usando regresión lineal 
    """
    sensor_type = reading["sensor_type"]
    value = reading["value"]
    sensor_id = reading["sensor_id"]

    min_val = THRESHOLDS[sensor_type]["min"]
    max_val = THRESHOLDS[sensor_type]["max"]
    
    last_N = history.get(sensor_id, [])

    # Validación básica si no hay historial suficiente
    if len(last_N) < MIN_HISTORY:
        if value < min_val or value > max_val:
            return "out_of_range"
        return None

    # Array NumPy para operaciones vectorizadas
    values_array = np.array(last_N)

    # 1. SPIKE: Detección estadística por Z-score
    # Si el valor actual se aleja más de 3 desviaciones típicas de la media histórica
    mean = np.mean(values_array)
    std = np.std(values_array)
    if std > 0:
        z_score = abs(value-mean) / std
        if z_score > 3 and (value < min_val or value > max_val):
            return "spike"

    # 2. DRIFT y OUT_OF_RANGE: Anomalías explícitas 
        # Out Of Range: fuera de umbrales pero sin patrón estadístico claro
    if value < min_val or value > max_val:
        # Vectorización: comprobamos si todo el histórico reciente también falló
        if np.all((values_array < min_val) | (values_array > max_val)):
            return "drift"
        return "out_of_range"

    # 3. MANTENIMIENTO PREDICTIVO (Time-to-Threshold Warning)
    #Aún estamos dentro de los márgenes seguros, pero la tendencia puede ser crítica
    x = np.arange(len(values_array))
    slope, intercept = np.polyfit(x, values_array, 1)

    #Análisis de tendencia positiva (acercándose al límite máximo)
    if slope > 0:
        # y = m*x + c -> x = (y - c) / m
        steps_to_cross = (max_val - intercept) / slope
        future_steps = steps_to_cross - len(values_array)
        
        #Si los pasos futuros son menores a 15 Argus lanza una anomalía de mantenimiento preditivo
        #Con un mensaje crítico en la base de datos
        """
        Nota personal: 
        De esta manera pasamos de un sistema de monitoreo reactvo a uno predictivo dándole a los operadores
        IoT una ventana de tiempo antes de un fallo inminente para poder apagar y conservar la máquina 
        salvando costes
        """
        if 0 < future_steps <= 15 and value >= (max_val * 0.9):
            reading["notes"] = f"CRÍTICO: Límite superior en {int(future_steps)} iteraciones"
            return "predictive_warning"

    #Análisis de tendencia negativa (acercándose al límite mínimo)
    elif slope < 0:
        steps_to_cross = (min_val - intercept) / slope
        future_steps = steps_to_cross - len(values_array)
        
        # Fallará en los próximos 15 ciclos y ya está cerca del mínimo
        if 0 < future_steps <= 15 and value <= (min_val * 1.1):
            reading["notes"] = f"CRÍTICO: Caída bajo el límite en {int(future_steps)} iteraciones"
            return "predictive_warning"

    return None