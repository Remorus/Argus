# Arquitectura de Argus

## Flujo de datos

```
TurbineSimulator
      │
      │  generate_reading()
      ▼
  run_sensor()  ──────────────────────────────────────────┐
      │                                                    │
      │  Reading                                           │
      ▼                                                    │
   MySQL                                              analyzer.py
      │                                                    │
      │                                            anomaly_type?
      │                                                    │
      │                                             Anomaly (FK)
      │                                                    │
      └───────────────────┬────────────────────────────────┘
                          │
                       FastAPI
                          │
              ┌───────────┼───────────┐
              │           │           │
         /readings  /readings/    /anomalies
                    {sensor_id}
```

Tres threads corren en paralelo, uno por sensor, compartiendo una única instancia de `TurbineSimulator`. Esto es intencional: los sensores de una turbina real están correlacionados de manera que un fallo de vibración afecta a la temperatura, no son procesos independientes.

---

## Decisiones de diseño

**Una instancia de TurbineSimulator compartida entre threads**

El estado de la turbina (normal, overheating, vibration\_fault, power\_spike) es global. Si cada sensor tuviese su propio simulador, los fallos serían independientes y el sistema no tendría coherencia física.

**Tabla `anomaly` separada de `reading`**

Podría haberse añadido una columna `anomaly_type` a `reading`, pero mantener las anomalías en su propia tabla permite consultarlas directamente sin filtrar por NULL, y hace más limpio el modelo relacional. La relación es uno a uno mediante FK.

**Historial en memoria, no en MySQL**

El analizador necesita los últimos N valores de cada sensor para distinguir entre spike y drift. Hacer una query a MySQL en cada ciclo sería innecesariamente lento. El historial se guarda en el propio objeto `TurbineSimulator` como diccionario en memoria.

**Sesiones SQLAlchemy por lectura**

Cada ciclo de `run_sensor()` abre y cierra su propia sesión en lugar de mantener una sesión global. Esto evita problemas de concurrencia entre threads y es el patrón recomendado para aplicaciones con múltiples workers.

**Configuración centralizada en `config.py`**

Sensores, umbrales, intervalos y tipos de fallo están definidos en un único archivo. Cambiar el comportamiento del sistema no requiere tocar la lógica.

---

## Modelos de datos

```
Reading
├── id           INTEGER  PK
├── sensor_id    VARCHAR
├── sensor_type  VARCHAR
├── value        FLOAT
├── unit         VARCHAR
├── notes        VARCHAR  nullable  -- "Fallo resuelto: X" cuando un fallo persistente termina
└── timestamp    DATETIME

Anomaly
├── id           INTEGER  PK
├── anom_type    VARCHAR  -- spike | out_of_range | drift
└── owner_id     INTEGER  FK → Reading.id
```

---

## Lógica de detección de anomalías

El analizador recibe la lectura actual y el historial de los últimos 10 valores del sensor.

- Si el valor está dentro de los umbrales → no hay anomalía
- Si el valor está fuera de los umbrales:
  - Solo hay 1 valor fuera en el historial → `spike`
  - Hay varios valores fuera pero no todos → `out_of_range`
  - Todos los valores del historial están fuera → `drift`

---

## Estados de fallo del simulador

| Estado | Tipo | Recuperación |
|---|---|---|
| normal | — | — |
| power\_spike | Transitorio | Automática tras N ciclos |
| overheating | Persistente | Probabilidad 2% por ciclo |
| vibration\_fault | Persistente | Probabilidad 3% por ciclo |

Cuando un fallo persistente se resuelve, la lectura correspondiente incluye una nota en el campo `notes` de la tabla `reading`.