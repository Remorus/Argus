# Argus — Real-time IoT Sensor Monitoring System with Anomaly Detection

**Argus** es un sistema de monitoreo en tiempo real de sensores IoT con detección de anomalías, construido con **Python, FastAPI, MySQL y Docker**. Permite simular datos de sensores, almacenar lecturas en una base de datos, detectar anomalías (picos, deriva o valores fuera de rango) y generar alertas inmediatas, con visualización gráfica de los resultados.

En concreto, analizaremos **palas de una turbina de gas**, las cuales soportan los mayores esfuerzos térmicos. Su monitoreo garantiza eficiencia, seguridad y vida útil de la turbina.

---

## Parámetros a Analizar

| Parámetro                                    | Rango típico                          | Límite crítico         | Observaciones                                                                                                                   |
| -------------------------------------------- | ------------------------------------- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| **Temperatura (gases que impactan palas)**   | 1200–1400 °C                          | >1400 °C               | Indica el estrés térmico sobre las palas; valores mayores requieren revisión y control de enfriamiento.                         |
| **Potencia (Power / Output)**                | 24–35 MW (turbina industrial mediana) | Caídas súbitas >10–15% | Analiza eficiencia y posibles pérdidas por daño en palas o problemas de combustión.                                             |
| **Vibración (Vibration / Cojinetes y ejes)** | 3–8 mm/s r.m.s.                       | >8 mm/s                | Valores altos pueden indicar desbalance, desgaste de cojinetes o daño en palas; correlacionar con temperatura para diagnóstico. |

**Nota:** Los valores son representativos de turbinas de gas industriales típicas.
El análisis se centrará en la **correlación entre temperatura, potencia y vibración**, buscando tendencias y anomalías que puedan indicar riesgo de fallo o reducción de eficiencia.

---

## Características

* Simulación de datos de sensores con ruido y anomalías aleatorias.
* Detección de tres tipos de anomalías: **spike**, **deriva** y **fuera de rango**.
* API REST con **FastAPI** para acceder a datos y anomalías.
* Visualización de datos con **matplotlib**, incluyendo anomalías detectadas.
* Persistencia en **MySQL** con modelos definidos en **SQLAlchemy**.
* Arquitectura preparada para **dockerización** y despliegue escalable.
* Sistema modular y testeable para asegurar la calidad del código.

---

## Estructura del Proyecto

```
argus/
├── sensors/                        # Simulador de sensores
│    └── simulator.py               # Genera datos falsos con ruido y anomalías
├── storage/                        # Modelos y conexión a la base de datos
│    ├── models.py                  # Definición de tablas MySQL con SQLAlchemy
│    └── database.py                # Conexión a MySQL y operaciones CRUD
├── analysis/                       # Detección de anomalías
│    ├── analyzer.py                # Detecta picos, deriva y valores fuera de rango
│    └── alerts.py                  # Genera alertas en consola
├── api/                            # Servidor REST
│    ├── main.py                    # Arranca el servidor FastAPI
│    └── routes.py                  # Endpoints: /sensors, /readings, /anomalies
├── dashboard/                      # Visualización de datos
│    └── plot.py                    # Gráficas con anomalías marcadas
├── tests/                          # Test unitarios
│    ├── test_simulator.py          # Test del simulador de sensores
│    └── test_analyzer.py           # Test de detección de anomalías
└── docs/                            # Documentación
     └── architecture.md            # Explic
```
