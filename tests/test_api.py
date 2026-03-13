"""
Tests para la API
"""
import pytest
from src.api.app import create_app
from src.config import TestingConfig
from src.database.connection import SessionLocal, engine
from src.models.base import Base, Facultad, Carrera

@pytest.fixture
def app():
    """Crea una aplicación Flask para testing"""
    app = create_app(TestingConfig)
    
    # Crear tablas
    Base.metadata.create_all(bind=engine)
    
    yield app
    
    # Limpiar
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(app):
    """Crea un cliente de prueba"""
    return app.test_client()

@pytest.fixture
def db_test():
    """Crea una sesión de base de datos para pruebas"""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_health_check(client):
    """Prueba el endpoint de health check"""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert 'status' in data

def test_index(client):
    """Prueba la página de inicio"""
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert 'nombre' in data
    assert data['nombre'] == 'Practicas ITM - API'

def test_crear_facultad(client, db_test):
    """Prueba crear una facultad"""
    datos = {
        'nombre': 'Ingeniería',
        'descripcion': 'Facultad de Ingeniería'
    }
    
    response = client.post('/api/facultades/', json=datos)
    assert response.status_code == 201
    data = response.get_json()
    assert 'datos' in data
    assert data['datos']['nombre'] == 'Ingeniería'

def test_listar_facultades(client, db_test):
    """Prueba listar facultades"""
    # Crear una facultad
    facultad = Facultad(nombre="Ingeniería", descripcion="Facultad de Ingeniería")
    db_test.add(facultad)
    db_test.commit()
    
    response = client.get('/api/facultades/')
    assert response.status_code == 200
    data = response.get_json()
    assert 'datos' in data
    assert len(data['datos']) > 0

def test_endpoint_no_encontrado(client):
    """Prueba un endpoint que no existe"""
    response = client.get('/api/inexistente')
    assert response.status_code == 404
