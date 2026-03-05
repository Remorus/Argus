import random
import numpy as np
from datetime import datetime, timezone
from config import SENSORS, INTERVALS, THRESHOLDS, FAULT_TYPES, FAULT_PROBABILITY


class TurbineSimulator: 
    def __init__(self):
        self.state = "normal"   
        self.time_in_state = 0 
        self.fault_resolved = False         # Flag para notificar cuando se resuelve
    
    def get_state(self):
        """
        Actualiza el estado de la turbina.
        """
        self.fault_resolved = False
        self.time_in_state += 1
        
        # Si estamos en normal, existirá una pequeña probabilidad de entrar en fallo
        if self.state == "normal":
            if random.random() < FAULT_PROBABILITY:
                self.state = random.choice(list(FAULT_TYPES.keys()))
                self.time_in_state = 0
        
        else:
            fault = FAULT_TYPES[self.state]
            if not fault["persistent"]:
                # Fallo puntual: se cura solo con el tiempo
                if self.time_in_state > fault["max_duration"]: 
                    self.state = "normal"
                    self.time_in_state = 0 
                    self.fault_resolved = True
            else: 
                # Fallo Crítico: Se cura con Probabilidad
                if random.random() < fault["recovery_prob"]:
                    self.state = "normal"
                    self.time_in_state = 0 
                    self.fault_resolved = True

    
    def add_sensor_noise(self,value, noise_level):
        """
        Recibe valor base  y un nivel de ruido.
        Devuelve un valor con ruido gaussiano añadido
        """
        noise_value = value + np.random.normal(0, noise_level)
        return noise_value