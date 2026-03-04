"""
Gestión de la Conexión a la base de datos MySQL

Crea el engine, la sesión y la clase Base que
heredarán todos los modelos del proyecto
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base 
from sqlalchemy.orm import sessionmaker                 

from config import DATABASE_URL

# Conectamos Python con la base de datos
engine = create_engine(DATABASE_URL, echo=True)

# =========================================================================
# GESTIÓN DE SESIÓN:
    # autocommit=False -> no se guardan cambios automáticamente en DB
    # autoflush=False -> no envía cambios automáticamente antes de consultas
# =========================================================================
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para nuestros modelos
Base = declarative_base()


def get_db():
    """
    Genera una sesión de base de datos y la cierra al terminar
    """
    db = SessionLocal()
    try: 
        yield db
    finally: 
        db.close()