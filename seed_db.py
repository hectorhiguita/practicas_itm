"""
Script para popular la base de datos con datos de ejemplo
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.connection import get_session, engine
from src.models.base import Base
from src.services.facultad_service import FacultadService
from src.services.carrera_service import CarreraService
from src.services.estudiante_service import EstudianteService

def populate_database():
    """Popula la base de datos con datos de ejemplo"""
    
    print("=" * 60)
    print("POBLADOR DE BASE DE DATOS - Practicas ITM")
    print("=" * 60)
    
    db = get_session()
    
    try:
        # Crear facultades
        print("\n📚 Creando facultades...")
        
        facultades_data = [
            {
                'nombre': 'Ingeniería',
                'descripcion': 'Facultad de Ingeniería - Programas de ingeniería'
            },
            {
                'nombre': 'Administración',
                'descripcion': 'Facultad de Administración - Programas de administración'
            },
            {
                'nombre': 'Ciencias Exactas',
                'descripcion': 'Facultad de Ciencias Exactas - Programas de ciencias'
            }
        ]
        
        facultades = {}
        for fac_data in facultades_data:
            try:
                fac = FacultadService.crear_facultad(db, fac_data['nombre'], fac_data['descripcion'])
                facultades[fac_data['nombre']] = fac
                print(f"  ✓ Facultad '{fac_data['nombre']}' creada")
            except ValueError as e:
                print(f"  ℹ {fac_data['nombre']}: {e}")
        
        # Crear carreras
        print("\n🎓 Creando carreras...")
        
        carreras_data = [
            {
                'nombre': 'Ingeniería de Sistemas',
                'facultad': 'Ingeniería',
                'descripcion': 'Programa de Ingeniería de Sistemas'
            },
            {
                'nombre': 'Ingeniería Industrial',
                'facultad': 'Ingeniería',
                'descripcion': 'Programa de Ingeniería Industrial'
            },
            {
                'nombre': 'Ingeniería Mecánica',
                'facultad': 'Ingeniería',
                'descripcion': 'Programa de Ingeniería Mecánica'
            },
            {
                'nombre': 'Administración de Empresas',
                'facultad': 'Administración',
                'descripcion': 'Programa de Administración de Empresas'
            },
            {
                'nombre': 'Contabilidad',
                'facultad': 'Administración',
                'descripcion': 'Programa de Contabilidad'
            }
        ]
        
        # Obtener todas las facultades creadas
        from src.models.base import Facultad, Carrera
        facultades_db = db.query(Facultad).all()
        facultades_map = {f.nombre: f for f in facultades_db}
        
        carreras = {}
        for car_data in carreras_data:
            try:
                fac = facultades_map.get(car_data['facultad'])
                if not fac:
                    print(f"  ✗ Facultad '{car_data['facultad']}' no encontrada")
                    continue
                    
                car = CarreraService.crear_carrera(
                    db,
                    car_data['nombre'],
                    fac.id,
                    car_data['descripcion']
                )
                carreras[car_data['nombre']] = car
                print(f"  ✓ Carrera '{car_data['nombre']}' creada")
            except ValueError as e:
                print(f"  ℹ {car_data['nombre']}: {e}")
            except Exception as e:
                print(f"  ✗ Error: {str(e)}")
        
        # Crear estudiantes
        print("\n👨‍🎓 Creando estudiantes...")
        
        estudiantes_data = [
            {
                'numero_documento': '1001234567',
                'nombre': 'Juan',
                'apellido': 'Pérez',
                'email': 'juan.perez@example.com',
                'genero': 'Masculino',
                'carrera': 'Ingeniería de Sistemas',
                'telefono': '3001234567'
            },
            {
                'numero_documento': '1002345678',
                'nombre': 'María',
                'apellido': 'García',
                'email': 'maria.garcia@example.com',
                'genero': 'Femenino',
                'carrera': 'Ingeniería de Sistemas',
                'telefono': '3002345678'
            },
            {
                'numero_documento': '1003456789',
                'nombre': 'Carlos',
                'apellido': 'López',
                'email': 'carlos.lopez@example.com',
                'genero': 'Masculino',
                'carrera': 'Ingeniería Industrial',
                'telefono': '3003456789'
            },
            {
                'numero_documento': '1004567890',
                'nombre': 'Ana',
                'apellido': 'Martínez',
                'email': 'ana.martinez@example.com',
                'genero': 'Femenino',
                'carrera': 'Administración de Empresas',
                'telefono': '3004567890'
            },
            {
                'numero_documento': '1005678901',
                'nombre': 'Pedro',
                'apellido': 'González',
                'email': 'pedro.gonzalez@example.com',
                'genero': 'Masculino',
                'carrera': 'Contabilidad',
                'telefono': '3005678901'
            },
            {
                'numero_documento': '1006789012',
                'nombre': 'Laura',
                'apellido': 'Rodríguez',
                'email': 'laura.rodriguez@example.com',
                'genero': 'Femenino',
                'carrera': 'Ingeniería Mecánica',
                'telefono': '3006789012'
            }
        ]
        
        estudiantes_creados = []
        for est_data in estudiantes_data:
            try:
                # Obtener la carrera del diccionario
                car = carreras.get(est_data['carrera'])
                if not car:
                    print(f"  ✗ Carrera '{est_data['carrera']}' no encontrada")
                    continue
                
                est = EstudianteService.crear_estudiante(
                    db,
                    est_data['numero_documento'],
                    est_data['nombre'],
                    est_data['apellido'],
                    est_data['email'],
                    est_data['genero'],
                    car.facultad_id,
                    car.id,
                    est_data['telefono']
                )
                estudiantes_creados.append(est)
                print(f"  ✓ Estudiante '{est_data['nombre']} {est_data['apellido']}' creado")
            except ValueError as e:
                print(f"  ℹ {est_data['nombre']}: {e}")
            except Exception as e:
                print(f"  ✗ Error creando {est_data['nombre']}: {str(e)}")
        
        # Actualizar algunos estados
        print("\n🔄 Actualizando estados de prácticas...")
        
        if len(estudiantes_creados) > 0:
            EstudianteService.actualizar_estado_practica(
                db, estudiantes_creados[0].id, 'Contratado'
            )
            print(f"  ✓ {estudiantes_creados[0].nombre} -> Contratado")
        
        if len(estudiantes_creados) > 1:
            EstudianteService.actualizar_estado_practica(
                db, estudiantes_creados[1].id, 'Por Finalizar'
            )
            print(f"  ✓ {estudiantes_creados[1].nombre} -> Por Finalizar")
        
        if len(estudiantes_creados) > 2:
            EstudianteService.actualizar_estado_practica(
                db, estudiantes_creados[2].id, 'Finalizó'
            )
            print(f"  ✓ {estudiantes_creados[2].nombre} -> Finalizó")
        
        print("\n" + "=" * 60)
        print("✓ Base de datos poblada correctamente")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_database()
