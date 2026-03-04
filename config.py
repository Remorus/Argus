# =========================================
# CONFIGURACIÓN del SISTEMA
# =========================================
import os 
from dotenv import load_dotenv
from sqlalchemy import create_engine

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
engine = create_engine(DATABASE_URL, echo = True) # Esto nos permite conectar Python con la base de datos. 


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
    "temperature": {"min":1200, "max":1400},     # ºC
    "power": {"min": 20,"max": 35},                         # MW
    "vibration":{"min": 3,"max": 8}                        #mm/s
}
