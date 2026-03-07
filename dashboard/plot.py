from storage.database import SessionLocal
from storage.models import Reading, Anomaly
import matplotlib.pyplot as plt
from config import THRESHOLDS


# Abrimos sesión de base de datos 
def plot_sensor(sensor_id:str):
    db = SessionLocal()
    try:
        # Lecturas de un sensor específico
        readings = db.query(Reading).filter(Reading.sensor_id==sensor_id).order_by(Reading.timestamp.desc()).limit(100).all()
        # Anomalías de ese sensor
        reading_id = [r.id for r in readings]
        anomalies = db.query(Anomaly).filter(Anomaly.owner_id.in_(reading_id)).all()
        


        # ---------
        # PINTAMOS
        # ---------
            # VALORES PARA PINTAR
        timestamps = [r.timestamp for r in readings]
        values = [r.value for r in readings]

        anomaly_ids = {a.owner_id for a in anomalies}
        anom_timestamps = [r.timestamp for r in readings if r.id in anomaly_ids]
        anom_values = [r.value for r in readings if r.id in anomaly_ids]

            # DIBUJAMOS
        fig, ax = plt.subplots(figsize=(14, 6))
        fig.patch.set_facecolor("#1e1e2e")
        ax.set_facecolor("#1e1e2e")
        
        ax.axhline(y=THRESHOLDS[readings[0].sensor_type]["max"], color="#ff9800", linewidth=1, linestyle="--", label="Umbral máximo")
        ax.axhline(y=THRESHOLDS[readings[0].sensor_type]["min"], color="#ff9800", linewidth=1, linestyle="--", label="Umbral mínimo")
        ax.plot(timestamps, values, color="#4fc3f7", linewidth=1.5, label="Lectura normal")
        ax.scatter(anom_timestamps, anom_values, color="#ff5252", s=80, zorder=5, label="Anomalía detectada")

        ax.set_title(f"Sensor: {sensor_id}", color="white", fontsize=14)
        ax.set_xlabel("Tiempo", color="white")
        ax.set_ylabel(f"Valor ({readings[0].unit})", color="white")
        ax.tick_params(colors="white")
        ax.legend(facecolor="#2e2e3e", labelcolor="white")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"dashboard/{sensor_id}.png", dpi=150)
        plt.show()
    finally:
        db.close()