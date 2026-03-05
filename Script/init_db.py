"""
Script Auxiliar: 
Crea las tablas en MySQL la primera vez que arrancamos el proyecto

> Notas Personales: 
Solo se ejecutará una vez. Luego lo importaremos desde Main.
"""


from storage.database import engine, Base
import storage.models # Importamos los modelos creados

def init_db():
    Base.metadata.create_all(bind = engine)   
