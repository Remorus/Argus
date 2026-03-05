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

    def simulate_temperature(self):
        """
        Devuelve un valor de temperatura realista
        según el estado actual de la turbina.
        -----------------------------------
        Ref:https://en.wikipedia.org/wiki/Combined-cycle_power_plant
        """

        min_temp = THRESHOLDS["temperature"]["min"]
        max_temp = THRESHOLDS["temperature"]["max"]

        mu = (min_temp + max_temp) / 2
        sigma = (max_temp-min_temp) / 6     # El 99 % caerá dentro del rango 

        
        if self.state == "normal":
            # Valor razonable de funcionamiento
            temperature = random.gauss(mu, sigma)
        elif self.state == "power_spike":
            # Suponemos correlación entre Power_Spike y Tª proporcional
            temperature = random.gauss (mu +20 , sigma)
        elif self.state == "vibration_fault":
            # Correlación: Sube moderadamente con el tiempo por fricción
            temperature = random.gauss(mu+ self.time_in_state*2,sigma)
        else:
            # Caso Overheating: Sube rápido y de forma crítica
            temperature = random.gauss(mu + self.time_in_state*5, sigma)
        
        return self.add_sensor_noise(temperature, 10)   # Agregamos ruido

    def simulate_power(self):
        """
        Devuelve un valor de potencia realista
        según el estado actual de la turbina.
        -----------------------------------
        Ref:https://en.wikipedia.org/wiki/Combined-cycle_power_plant
        """

        min_pw = THRESHOLDS["power"]["min"]
        max_pw = THRESHOLDS["power"]["max"]

        mu = (min_pw + max_pw) / 2
        sigma = (max_pw-min_pw) / 6     

        
        if self.state in ["normal", "vibration_fault"]:
            # Valor razonable de funcionamiento
            pw = random.gauss(mu, sigma)
        elif self.state == "overheating":
            # Turbina reduce potencia para intentar enfriarse: Correlación inversa
            pw = random.gauss (mu - 20 , sigma)
        else:
            # Caso power_spike: Sube rápido y de forma crítica
            pw = random.gauss(mu + self.time_in_state*5, sigma)
        
        return self.add_sensor_noise(pw, 3)   # Agregamos ruido
    