"""
Tests para el servicio de estudiantes
"""
import pytest
from src.database.connection import SessionLocal, engine
from src.models.base import Base, Facultad, Carrera, Estudiante
from src.services.estudiante_service import EstudianteService
from src.utils.enums import Genero, EstadoPractica

@pytest.fixture
def db():
    """Crea una nueva base de datos de test para cada test"""
    # Crear tablas
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    
    yield session
    
    # Limpiar después del test
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def facultad_test(db):
    """Crea una facultad de prueba"""
    facultad = Facultad(nombre="Ingeniería", descripcion="Facultad de Ingeniería")
    db.add(facultad)
    db.commit()
    db.refresh(facultad)
    return facultad

@pytest.fixture
def carrera_test(db, facultad_test):
    """Crea una carrera de prueba"""
    carrera = Carrera(
        nombre="Ingeniería de Sistemas",
        facultad_id=facultad_test.id,
        descripcion="Carrera de Ingeniería de Sistemas",
        nivel="Ingeniería",
        duracion="10 semestres",
        perfil_profesional="Desarrollo y gestión de sistemas de información"
    )
    db.add(carrera)
    db.commit()
    db.refresh(carrera)
    return carrera

def test_crear_estudiante(db, facultad_test, carrera_test):
    """Prueba la creación de un estudiante"""
    estudiante = EstudianteService.crear_estudiante(
        db=db,
        numero_documento="12345678",
        nombre="Juan",
        apellido="Pérez",
        email="juan@example.com",
        genero="Masculino",
        facultad_id=facultad_test.id,
        carrera_id=carrera_test.id
    )
    
    assert estudiante.id is not None
    assert estudiante.numero_documento == "12345678"
    assert estudiante.nombre == "Juan"
    assert estudiante.estado_practica == EstadoPractica.DISPONIBLE

def test_obtener_estudiante(db, facultad_test, carrera_test):
    """Prueba obtener un estudiante"""
    # Crear estudiante
    estudiante_creado = EstudianteService.crear_estudiante(
        db=db,
        numero_documento="12345678",
        nombre="Juan",
        apellido="Pérez",
        email="juan@example.com",
        genero="Masculino",
        facultad_id=facultad_test.id,
        carrera_id=carrera_test.id
    )
    
    # Obtener estudiante
    estudiante = EstudianteService.obtener_estudiante(db, estudiante_creado.id)
    
    assert estudiante is not None
    assert estudiante.id == estudiante_creado.id
    assert estudiante.nombre == "Juan"

def test_actualizar_estado_practica(db, facultad_test, carrera_test):
    """Prueba actualizar el estado de práctica"""
    # Crear estudiante
    estudiante_creado = EstudianteService.crear_estudiante(
        db=db,
        numero_documento="12345678",
        nombre="Juan",
        apellido="Pérez",
        email="juan@example.com",
        genero="Masculino",
        facultad_id=facultad_test.id,
        carrera_id=carrera_test.id
    )
    
    # Actualizar estado
    estudiante_actualizado = EstudianteService.actualizar_estado_practica(
        db=db,
        estudiante_id=estudiante_creado.id,
        nuevo_estado="Contratado"
    )
    
    assert estudiante_actualizado.estado_practica == EstadoPractica.CONTRATADO

def test_obtener_estudiantes_disponibles(db, facultad_test, carrera_test):
    """Prueba obtener estudiantes disponibles"""
    # Crear dos estudiantes
    estudiante1 = EstudianteService.crear_estudiante(
        db=db,
        numero_documento="12345678",
        nombre="Juan",
        apellido="Pérez",
        email="juan@example.com",
        genero="Masculino",
        facultad_id=facultad_test.id,
        carrera_id=carrera_test.id
    )
    
    estudiante2 = EstudianteService.crear_estudiante(
        db=db,
        numero_documento="87654321",
        nombre="María",
        apellido="García",
        email="maria@example.com",
        genero="Femenino",
        facultad_id=facultad_test.id,
        carrera_id=carrera_test.id
    )
    
    # Cambiar estado del segundo a Contratado
    EstudianteService.actualizar_estado_practica(
        db=db,
        estudiante_id=estudiante2.id,
        nuevo_estado="Contratado"
    )
    
    # Obtener disponibles
    disponibles = EstudianteService.obtener_estudiantes_disponibles(db)
    
    assert len(disponibles) == 1
    assert disponibles[0].id == estudiante1.id

def test_eliminar_estudiante(db, facultad_test, carrera_test):
    """Prueba eliminar un estudiante"""
    # Crear estudiante
    estudiante = EstudianteService.crear_estudiante(
        db=db,
        numero_documento="12345678",
        nombre="Juan",
        apellido="Pérez",
        email="juan@example.com",
        genero="Masculino",
        facultad_id=facultad_test.id,
        carrera_id=carrera_test.id
    )
    
    # Eliminar
    resultado = EstudianteService.eliminar_estudiante(db, estudiante.id)
    
    assert resultado is True
    
    # Verificar que se eliminó
    estudiante_eliminado = EstudianteService.obtener_estudiante(db, estudiante.id)
    assert estudiante_eliminado is None
