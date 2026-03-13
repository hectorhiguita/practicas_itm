"""
Script para popular la base de datos con datos reales del ITM
Datos basados en el manual de marca ITM v2025
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.connection import get_session
from src.services.facultad_service import FacultadService
from src.services.carrera_service import CarreraService
from src.services.estudiante_service import EstudianteService
from src.utils.enums import EstadoPractica

def populate_database():
    """Popula la base de datos con datos reales del ITM"""
    
    print("=" * 80)
    print("POBLADOR DE BASE DE DATOS ITM - Sistema de Gestión de Prácticas")
    print("=" * 80)
    
    db = get_session()
    
    try:
        # ====== FACULTAD 1: ARTES Y HUMANIDADES ======
        print("\n📚 FACULTAD 1: Artes y Humanidades")
        print("-" * 80)
        
        facultad_artes = FacultadService.crear_facultad(
            db,
            'Facultad de Artes y Humanidades',
            'Campus La Floresta - Programas en artes, cine, música y diseño'
        )
        print(f"  ✓ Facultad creada: {facultad_artes.nombre}")
        
        carreras_artes = [
            {'nombre': 'Artes Visuales', 'nivel': 'Profesional', 'duracion': '9 semestres'},
            {'nombre': 'Cine', 'nivel': 'Profesional', 'duracion': '9 semestres'},
            {'nombre': 'Artes de la Grabación y Producción Musical', 'nivel': 'Profesional', 'duracion': '10 semestres'},
            {'nombre': 'Tecnología en Informática Musical', 'nivel': 'Tecnología', 'duracion': '6 semestres'},
            {'nombre': 'Tecnología en Diseño Industrial', 'nivel': 'Tecnología', 'duracion': '6 semestres'},
            {'nombre': 'Ingeniería en Diseño Industrial', 'nivel': 'Ingeniería', 'duracion': '10 semestres'},
        ]
        
        for carrera in carreras_artes:
            try:
                c = CarreraService.crear_carrera(
                    db,
                    carrera['nombre'],
                    facultad_artes.id,
                    f"{carrera['nivel']} - {carrera['duracion']}"
                )
                print(f"    ✓ {carrera['nombre']} ({carrera['nivel']})")
            except ValueError as e:
                print(f"    ℹ {carrera['nombre']}: {str(e)}")
        
        # ====== FACULTAD 2: CIENCIAS ECONÓMICAS Y ADMINISTRATIVAS ======
        print("\n💼 FACULTAD 2: Ciencias Económicas y Administrativas")
        print("-" * 80)
        
        facultad_admin = FacultadService.crear_facultad(
            db,
            'Facultad de Ciencias Económicas y Administrativas',
            'Campus Fraternidad - Programas en administración, finanzas y negocios'
        )
        print(f"  ✓ Facultad creada: {facultad_admin.nombre}")
        
        carreras_admin = [
            {'nombre': 'Tecnología en Gestión Administrativa', 'nivel': 'Tecnología', 'duracion': '6 semestres'},
            {'nombre': 'Tecnología en Análisis de Costos y Presupuestos', 'nivel': 'Tecnología', 'duracion': '6 semestres'},
            {'nombre': 'Tecnología en Calidad', 'nivel': 'Tecnología', 'duracion': '6 semestres'},
            {'nombre': 'Tecnología en Producción', 'nivel': 'Tecnología', 'duracion': '6 semestres'},
            {'nombre': 'Administración Tecnológica', 'nivel': 'Profesional', 'duracion': '10 semestres'},
            {'nombre': 'Administración del Deporte', 'nivel': 'Profesional', 'duracion': '9 semestres'},
            {'nombre': 'Ingeniería Financiera y de Negocios', 'nivel': 'Ingeniería', 'duracion': '10 semestres'},
            {'nombre': 'Ingeniería de Producción', 'nivel': 'Ingeniería', 'duracion': '10 semestres'},
            {'nombre': 'Ingeniería de la Calidad', 'nivel': 'Ingeniería', 'duracion': '10 semestres'},
        ]
        
        for carrera in carreras_admin:
            try:
                c = CarreraService.crear_carrera(
                    db,
                    carrera['nombre'],
                    facultad_admin.id,
                    f"{carrera['nivel']} - {carrera['duracion']}"
                )
                print(f"    ✓ {carrera['nombre']} ({carrera['nivel']})")
            except ValueError as e:
                print(f"    ℹ {carrera['nombre']}: {str(e)}")
        
        # ====== FACULTAD 3: CIENCIAS EXACTAS Y APLICADAS ======
        print("\n🔬 FACULTAD 3: Ciencias Exactas y Aplicadas")
        print("-" * 80)
        
        facultad_exactas = FacultadService.crear_facultad(
            db,
            'Facultad de Ciencias Exactas y Aplicadas',
            'Campus Robledo - Programas en ciencias, salud y ambiente'
        )
        print(f"  ✓ Facultad creada: {facultad_exactas.nombre}")
        
        carreras_exactas = [
            {'nombre': 'Tecnología en Mantenimiento de Equipo Biomédico', 'nivel': 'Tecnología', 'duracion': '6 semestres'},
            {'nombre': 'Tecnología en Construcción de Acabados Arquitectónicos', 'nivel': 'Tecnología', 'duracion': '6 semestres'},
            {'nombre': 'Ingeniería Biomédica', 'nivel': 'Ingeniería', 'duracion': '10 semestres'},
            {'nombre': 'Ciencias Ambientales', 'nivel': 'Profesional', 'duracion': '9 semestres'},
            {'nombre': 'Ciencia y Tecnología de los Alimentos', 'nivel': 'Profesional', 'duracion': '10 semestres'},
            {'nombre': 'Física', 'nivel': 'Profesional', 'duracion': '10 semestres'},
            {'nombre': 'Química Industrial', 'nivel': 'Profesional', 'duracion': '10 semestres'},
        ]
        
        for carrera in carreras_exactas:
            try:
                c = CarreraService.crear_carrera(
                    db,
                    carrera['nombre'],
                    facultad_exactas.id,
                    f"{carrera['nivel']} - {carrera['duracion']}"
                )
                print(f"    ✓ {carrera['nombre']} ({carrera['nivel']})")
            except ValueError as e:
                print(f"    ℹ {carrera['nombre']}: {str(e)}")
        
        # ====== FACULTAD 4: INGENIERÍAS ======
        print("\n⚙️  FACULTAD 4: Ingenierías")
        print("-" * 80)
        
        facultad_ingenieria = FacultadService.crear_facultad(
            db,
            'Facultad de Ingenierías',
            'Campus Robledo - Programas en ingeniería, tecnología e informática'
        )
        print(f"  ✓ Facultad creada: {facultad_ingenieria.nombre}")
        
        carreras_ingenieria = [
            {'nombre': 'Tecnología en Sistemas de Información', 'nivel': 'Tecnología', 'duracion': '6 semestres'},
            {'nombre': 'Tecnología en Telecomunicaciones', 'nivel': 'Tecnología', 'duracion': '6 semestres'},
            {'nombre': 'Tecnología en Electrónica', 'nivel': 'Tecnología', 'duracion': '6 semestres'},
            {'nombre': 'Tecnología en Sistemas Electromecánicos', 'nivel': 'Tecnología', 'duracion': '6 semestres'},
            {'nombre': 'Tecnología en Sistemas de Producción', 'nivel': 'Tecnología', 'duracion': '6 semestres'},
            {'nombre': 'Ingeniería de Sistemas', 'nivel': 'Ingeniería', 'duracion': '10 semestres'},
            {'nombre': 'Ingeniería de Telecomunicaciones', 'nivel': 'Ingeniería', 'duracion': '10 semestres'},
            {'nombre': 'Ingeniería Electrónica', 'nivel': 'Ingeniería', 'duracion': '10 semestres'},
            {'nombre': 'Ingeniería Electromecánica', 'nivel': 'Ingeniería', 'duracion': '10 semestres'},
            {'nombre': 'Interpretación y Traducción Lengua de Señas – Español', 'nivel': 'Profesional', 'duracion': '8 semestres'},
        ]
        
        for carrera in carreras_ingenieria:
            try:
                c = CarreraService.crear_carrera(
                    db,
                    carrera['nombre'],
                    facultad_ingenieria.id,
                    f"{carrera['nivel']} - {carrera['duracion']}"
                )
                print(f"    ✓ {carrera['nombre']} ({carrera['nivel']})")
            except ValueError as e:
                print(f"    ℹ {carrera['nombre']}: {str(e)}")
        
        # ====== ESTUDIANTES DE EJEMPLO ======
        print("\n👥 CREANDO ESTUDIANTES DE EJEMPLO")
        print("-" * 80)
        
        estudiantes_data = [
            {
                'documento': '1001234567',
                'nombre': 'Juan',
                'apellido': 'García',
                'email': 'juan.garcia@itm.edu.co',
                'telefono': '3001234567',
                'genero': 'Masculino',
                'carrera_id': 1,  # Primera carrera
                'estado': 'Disponible'
            },
            {
                'documento': '1002345678',
                'nombre': 'María',
                'apellido': 'López',
                'email': 'maria.lopez@itm.edu.co',
                'telefono': '3012345678',
                'genero': 'Femenino',
                'carrera_id': 2,
                'estado': 'Disponible'
            },
            {
                'documento': '1003456789',
                'nombre': 'Carlos',
                'apellido': 'Rodríguez',
                'email': 'carlos.rodriguez@itm.edu.co',
                'telefono': '3023456789',
                'genero': 'No Binario',
                'carrera_id': 3,
                'estado': 'Contratado'
            },
        ]
        
        for est_data in estudiantes_data:
            try:
                est = EstudianteService.crear_estudiante(
                    db,
                    numero_documento=est_data['documento'],
                    nombre=est_data['nombre'],
                    apellido=est_data['apellido'],
                    email=est_data['email'],
                    telefono=est_data['telefono'],
                    genero=est_data['genero'],
                    carrera_id=est_data['carrera_id']
                )
                
                # Actualizar estado si es diferente a Disponible
                if est_data['estado'] != 'Disponible':
                    EstudianteService.actualizar_estado_practica(
                        db,
                        est.id,
                        est_data['estado']
                    )
                
                print(f"  ✓ {est_data['nombre']} {est_data['apellido']} ({est_data['estado']})")
            except ValueError as e:
                print(f"  ℹ {est_data['nombre']} {est_data['apellido']}: {str(e)}")
        
        print("\n" + "=" * 80)
        print("✅ BASE DE DATOS POBLADA EXITOSAMENTE")
        print("=" * 80)
        print("\n📊 RESUMEN:")
        print(f"  • Facultades: 4")
        print(f"  • Carreras: {sum(len(c) for c in [carreras_artes, carreras_admin, carreras_exactas, carreras_ingenieria])}")
        print(f"  • Estudiantes de ejemplo: {len(estudiantes_data)}")
        print("\n🚀 La aplicación está lista para usar!")
        print("   Accede a: http://localhost:5000")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    # Primero, crear tablas si no existen
    from src.database.init_db import init_database
    print("Inicializando base de datos...")
    init_database()
    print("✓ Base de datos inicializada\n")
    
    # Ahora popular con datos
    populate_database()
