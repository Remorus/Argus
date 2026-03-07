# =========================================
# CONFIGURACIÓN del SISTEMA
# =========================================
import os 
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------
# CREDENCIALES del DB
# ---------------------------------------------
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}" # Usaré MySQL


# ---------------------------------------------
# Credenciales para API
# ---------------------------------------------
API_HOST = os.getenv("API_HOST")
API_PORT = int(os.getenv("API_PORT"))
# ---------------------------------------------
# SENSORES del SISTEMA
# Analizaremos las palas de turbina de gas 
# ---------------------------------------------

SENSORS = [
    {"id": "temp_turbine_01", "type": "temperature", "location": "Generator Room"},
    {"id": "pow_turbine_01",  "type": "power",       "location": "Generator Room"},
    {"id": "vib_turbine_01",  "type": "vibration",   "location": "Generator Room"},
]

INTERVALS ={
    "temperature" : 5, 
    "power" : 10, 
    "vibration" : 2,
}

THRESHOLDS = {
    "temperature": {"min":900, "max":1400},     # ºC
    "power": {"min": 100,"max": 300},                         # MW
    "vibration":{"min": 3,"max": 8}                        #mm/s
}


# ---------------------------------------------
# TIPOS DE FALLO
# ---------------------------------------------
FAULT_TYPES = {
    "power_spike": {
        "persistent": False,
        "max_duration": 5,        # ciclos
        "recovery_prob": 1.0      # se cura solo siempre
    },
    "overheating": {
        "persistent": True,
        "max_duration": None,
        "recovery_prob": 0.02     # 2% de probabilidad por ciclo
    },
    "vibration_fault": {
        "persistent": True,
        "max_duration": None,
        "recovery_prob": 0.03     # 3% de probabilidad por ciclo
    },
}

# Probabilidad de que ocurra un fallo en cada ciclo normal
FAULT_PROBABILITY = 0.1   # 10% por ciclo