"""
Tests para la base de datos
"""
import pytest
from sqlalchemy import inspect
from src.database.connection import test_connection, SessionLocal, engine
from src.models.base import Base, Facultad

def test_conexion_base_datos():
    """Prueba la conexión a la base de datos"""
    resultado = test_connection()
    assert resultado is True

def test_crear_tablas():
    """Prueba la creación de tablas"""
    # Crear tablas
    Base.metadata.create_all(bind=engine)
    
    # Verificar que existen
    inspector = inspect(engine)
    tablas = inspector.get_table_names()
    
    assert 'facultades' in tablas
    assert 'carreras' in tablas
    assert 'estudiantes' in tablas
    
    # Limpiar
    Base.metadata.drop_all(bind=engine)

def test_crear_facultad():
    """Prueba crear una facultad"""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    
    facultad = Facultad(nombre="Ingeniería", descripcion="Facultad de Ingeniería")
    session.add(facultad)
    session.commit()
    session.refresh(facultad)
    
    assert facultad.id is not None
    assert facultad.nombre == "Ingeniería"
    
    session.close()
    Base.metadata.drop_all(bind=engine)
