"""
Gestión de conexión a la base de datos
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from src.config import get_config

config = get_config()

# Crear engine
engine = create_engine(
    config.SQLALCHEMY_DATABASE_URI,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Crear factory de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session() -> Session:
    """
    Obtiene una nueva sesión de base de datos
    
    Returns:
        Session: Sesión de SQLAlchemy
    """
    return SessionLocal()

def get_db():
    """
    Generador de sesión para usar con dependencias en Flask
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Inicializa la base de datos creando todas las tablas
    """
    from src.models.base import Base
    Base.metadata.create_all(bind=engine)

def test_connection():
    """
    Prueba la conexión a la base de datos
    
    Returns:
        bool: True si la conexión es exitosa
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return result.fetchone() is not None
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return False
