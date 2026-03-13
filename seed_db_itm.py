"""
Script para popular la base de datos con datos reales del ITM
Datos basados en el manual de marca ITM v2025
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.connection import get_session
from src.services.facultad_service import FacultadService
from src.services.programa_service import ProgramaService
from src.services.estudiante_service import EstudianteService


def populate_database():
    """Popula la base de datos con datos reales del ITM"""

    print("=" * 80)
    print("POBLADOR DE BASE DE DATOS ITM - Sistema de Gestión de Prácticas")
    print("=" * 80)

    db = get_session()

    try:
        # ====== FACULTAD 1: ARTES Y HUMANIDADES ======
        print("\nFACULTAD 1: Artes y Humanidades")
        print("-" * 80)

        facultad_artes = FacultadService.crear_facultad(
            db,
            'Facultad de Artes y Humanidades',
            'Campus La Floresta - Programas en artes, cine, música y diseño'
        )
        print(f"  Facultad creada: {facultad_artes.nombre}")

        programas_artes = [
            {
                'nombre': 'Artes Visuales',
                'nivel': 'Profesional',
                'duracion': '9 semestres',
                'perfil_profesional': 'Profesional con capacidad creativa en artes visuales, diseño y producción artística.',
                'acreditada': False,
                'virtual': False,
            },
            {
                'nombre': 'Cine',
                'nivel': 'Profesional',
                'duracion': '9 semestres',
                'perfil_profesional': 'Profesional en realización cinematográfica, dirección, guión y producción audiovisual.',
                'acreditada': False,
                'virtual': False,
            },
            {
                'nombre': 'Artes de la Grabación y Producción Musical',
                'nivel': 'Profesional',
                'duracion': '10 semestres',
                'perfil_profesional': 'Profesional en grabación, mezcla, masterización y producción musical.',
                'acreditada': False,
                'virtual': False,
            },
            {
                'nombre': 'Tecnología en Informática Musical',
                'nivel': 'Tecnología',
                'duracion': '6 semestres',
                'perfil_profesional': 'Tecnólogo en producción musical digital, síntesis sonora y software musical.',
                'acreditada': False,
                'virtual': False,
            },
            {
                'nombre': 'Tecnología en Diseño Industrial',
                'nivel': 'Tecnología',
                'duracion': '6 semestres',
                'perfil_profesional': 'Tecnólogo capaz de diseñar y desarrollar productos industriales con enfoque creativo.',
                'acreditada': False,
                'virtual': False,
            },
            {
                'nombre': 'Ingeniería en Diseño Industrial',
                'nivel': 'Ingeniería',
                'duracion': '10 semestres',
                'perfil_profesional': 'Ingeniero en diseño de productos, con visión integral de manufactura y estética.',
                'acreditada': False,
                'virtual': False,
            },
        ]

        for prog in programas_artes:
            try:
                ProgramaService.crear_programa(
                    db,
                    nombre=prog['nombre'],
                    nivel=prog['nivel'],
                    facultad_id=facultad_artes.id,
                    duracion=prog['duracion'],
                    perfil_profesional=prog['perfil_profesional'],
                    acreditada=prog['acreditada'],
                    virtual=prog['virtual'],
                )
                print(f"    {prog['nombre']} ({prog['nivel']})")
            except Exception as e:
                print(f"    {prog['nombre']}: {str(e)}")

        # ====== FACULTAD 2: CIENCIAS ECONÓMICAS Y ADMINISTRATIVAS ======
        print("\nFACULTAD 2: Ciencias Económicas y Administrativas")
        print("-" * 80)

        facultad_admin = FacultadService.crear_facultad(
            db,
            'Facultad de Ciencias Económicas y Administrativas',
            'Campus Fraternidad - Programas en administración, finanzas y negocios'
        )
        print(f"  Facultad creada: {facultad_admin.nombre}")

        programas_admin = [
            {
                'nombre': 'Tecnología en Gestión Administrativa',
                'nivel': 'Tecnología',
                'duracion': '6 semestres',
                'perfil_profesional': 'Tecnólogo con habilidades en planeación, organización y control de procesos administrativos.',
                'acreditada': False,
                'virtual': False,
            },
            {
                'nombre': 'Tecnología en Análisis de Costos y Presupuestos',
                'nivel': 'Tecnología',
                'duracion': '6 semestres',
                'perfil_profesional': 'Tecnólogo especializado en análisis financiero, costos y presupuestos empresariales.',
                'acreditada': False,
                'virtual': False,
            },
            {
                'nombre': 'Tecnología en Calidad',
                'nivel': 'Tecnología',
                'duracion': '6 semestres',
                'perfil_profesional': 'Tecnólogo en sistemas de gestión de calidad, normas ISO y mejora continua.',
                'acreditada': False,
                'virtual': False,
            },
            {
                'nombre': 'Tecnología en Producción',
                'nivel': 'Tecnología',
                'duracion': '6 semestres',
                'perfil_profesional': 'Tecnólogo en gestión y optimización de procesos productivos industriales.',
                'acreditada': False,
                'virtual': False,
            },
            {
                'nombre': 'Administración Tecnológica',
                'nivel': 'Profesional',
                'duracion': '10 semestres',
                'perfil_profesional': 'Profesional en gestión empresarial con énfasis en tecnología e innovación.',
                'acreditada': True,
                'virtual': False,
            },
            {
                'nombre': 'Administración del Deporte',
                'nivel': 'Profesional',
                'duracion': '9 semestres',
                'perfil_profesional': 'Profesional en gestión de organizaciones deportivas, eventos y proyectos del sector.',
                'acreditada': False,
                'virtual': False,
            },
            {
                'nombre': 'Ingeniería Financiera y de Negocios',
                'nivel': 'Ingeniería',
                'duracion': '10 semestres',
                'perfil_profesional': 'Ingeniero con capacidad de análisis financiero y toma de decisiones estratégicas de negocio.',
                'acreditada': True,
                'virtual': False,
            },
            {
                'nombre': 'Ingeniería de Producción',
                'nivel': 'Ingeniería',
                'duracion': '10 semestres',
                'perfil_profesional': 'Ingeniero en diseño y gestión de sistemas productivos y cadenas de suministro.',
                'acreditada': True,
                'virtual': False,
            },
            {
                'nombre': 'Ingeniería de la Calidad',
                'nivel': 'Ingeniería',
                'duracion': '10 semestres',
                'perfil_profesional': 'Ingeniero especializado en sistemas de gestión de calidad, auditorías y mejora de procesos.',
                'acreditada': False,
                'virtual': False,
            },
        ]

        for prog in programas_admin:
            try:
                ProgramaService.crear_programa(
                    db,
                    nombre=prog['nombre'],
                    nivel=prog['nivel'],
                    facultad_id=facultad_admin.id,
                    duracion=prog['duracion'],
                    perfil_profesional=prog['perfil_profesional'],
                    acreditada=prog['acreditada'],
                    virtual=prog['virtual'],
                )
                print(f"    {prog['nombre']} ({prog['nivel']})")
            except Exception as e:
                print(f"    {prog['nombre']}: {str(e)}")

        # ====== FACULTAD 3: CIENCIAS EXACTAS Y APLICADAS ======
        print("\nFACULTAD 3: Ciencias Exactas y Aplicadas")
        print("-" * 80)

        facultad_exactas = FacultadService.crear_facultad(
            db,
            'Facultad de Ciencias Exactas y Aplicadas',
            'Campus Robledo - Programas en ciencias, salud y ambiente'
        )
        print(f"  Facultad creada: {facultad_exactas.nombre}")

        programas_exactas = [
            {
                'nombre': 'Tecnología en Mantenimiento de Equipo Biomédico',
                'nivel': 'Tecnología',
                'duracion': '6 semestres',
                'perfil_profesional': 'Tecnólogo en mantenimiento preventivo y correctivo de equipos biomédicos hospitalarios.',
                'acreditada': False,
                'virtual': False,
            },
            {
                'nombre': 'Tecnología en Construcción de Acabados Arquitectónicos',
                'nivel': 'Tecnología',
                'duracion': '6 semestres',
                'perfil_profesional': 'Tecnólogo en procesos constructivos, acabados y gestión de obras arquitectónicas.',
                'acreditada': False,
                'virtual': False,
            },
            {
                'nombre': 'Ingeniería Biomédica',
                'nivel': 'Ingeniería',
                'duracion': '10 semestres',
                'perfil_profesional': 'Ingeniero en diseño e implementación de tecnología médica y sistemas de salud.',
                'acreditada': True,
                'virtual': False,
            },
            {
                'nombre': 'Ciencias Ambientales',
                'nivel': 'Profesional',
                'duracion': '9 semestres',
                'perfil_profesional': 'Profesional en gestión ambiental, conservación de ecosistemas y desarrollo sostenible.',
                'acreditada': False,
                'virtual': False,
            },
            {
                'nombre': 'Ciencia y Tecnología de los Alimentos',
                'nivel': 'Profesional',
                'duracion': '10 semestres',
                'perfil_profesional': 'Profesional en procesamiento, control de calidad y seguridad alimentaria.',
                'acreditada': False,
                'virtual': False,
            },
            {
                'nombre': 'Física',
                'nivel': 'Profesional',
                'duracion': '10 semestres',
                'perfil_profesional': 'Profesional con formación en física teórica y aplicada, investigación científica.',
                'acreditada': False,
                'virtual': False,
            },
            {
                'nombre': 'Química Industrial',
                'nivel': 'Profesional',
                'duracion': '10 semestres',
                'perfil_profesional': 'Profesional en procesos químicos industriales, control de calidad y gestión ambiental.',
                'acreditada': False,
                'virtual': False,
            },
        ]

        for prog in programas_exactas:
            try:
                ProgramaService.crear_programa(
                    db,
                    nombre=prog['nombre'],
                    nivel=prog['nivel'],
                    facultad_id=facultad_exactas.id,
                    duracion=prog['duracion'],
                    perfil_profesional=prog['perfil_profesional'],
                    acreditada=prog['acreditada'],
                    virtual=prog['virtual'],
                )
                print(f"    {prog['nombre']} ({prog['nivel']})")
            except Exception as e:
                print(f"    {prog['nombre']}: {str(e)}")

        # ====== FACULTAD 4: INGENIERÍAS ======
        print("\nFACULTAD 4: Ingenierías")
        print("-" * 80)

        facultad_ingenieria = FacultadService.crear_facultad(
            db,
            'Facultad de Ingenierías',
            'Campus Robledo - Programas en ingeniería, tecnología e informática'
        )
        print(f"  Facultad creada: {facultad_ingenieria.nombre}")

        programas_ingenieria = [
            {
                'nombre': 'Tecnología en Sistemas de Información',
                'nivel': 'Tecnología',
                'duracion': '6 semestres',
                'perfil_profesional': 'Tecnólogo en desarrollo de software, bases de datos y soporte de sistemas informáticos.',
                'acreditada': False,
                'virtual': False,
            },
            {
                'nombre': 'Tecnología en Telecomunicaciones',
                'nivel': 'Tecnología',
                'duracion': '6 semestres',
                'perfil_profesional': 'Tecnólogo en redes de comunicación, configuración de equipos y transmisión de datos.',
                'acreditada': False,
                'virtual': False,
            },
            {
                'nombre': 'Tecnología en Electrónica',
                'nivel': 'Tecnología',
                'duracion': '6 semestres',
                'perfil_profesional': 'Tecnólogo en diseño, montaje y mantenimiento de circuitos y sistemas electrónicos.',
                'acreditada': False,
                'virtual': False,
            },
            {
                'nombre': 'Tecnología en Sistemas Electromecánicos',
                'nivel': 'Tecnología',
                'duracion': '6 semestres',
                'perfil_profesional': 'Tecnólogo en instalación y mantenimiento de sistemas eléctricos y mecánicos industriales.',
                'acreditada': False,
                'virtual': False,
            },
            {
                'nombre': 'Tecnología en Sistemas de Producción',
                'nivel': 'Tecnología',
                'duracion': '6 semestres',
                'perfil_profesional': 'Tecnólogo en automatización y control de procesos productivos industriales.',
                'acreditada': False,
                'virtual': False,
            },
            {
                'nombre': 'Ingeniería de Sistemas',
                'nivel': 'Ingeniería',
                'duracion': '10 semestres',
                'perfil_profesional': 'Ingeniero con habilidades en desarrollo de software, arquitectura de sistemas y liderazgo tecnológico.',
                'acreditada': True,
                'virtual': False,
            },
            {
                'nombre': 'Ingeniería de Telecomunicaciones',
                'nivel': 'Ingeniería',
                'duracion': '10 semestres',
                'perfil_profesional': 'Ingeniero en diseño e implementación de redes, sistemas de comunicación y telecomunicaciones.',
                'acreditada': True,
                'virtual': False,
            },
            {
                'nombre': 'Ingeniería Electrónica',
                'nivel': 'Ingeniería',
                'duracion': '10 semestres',
                'perfil_profesional': 'Ingeniero en diseño de sistemas electrónicos, microcontroladores y procesamiento de señales.',
                'acreditada': True,
                'virtual': False,
            },
            {
                'nombre': 'Ingeniería Electromecánica',
                'nivel': 'Ingeniería',
                'duracion': '10 semestres',
                'perfil_profesional': 'Ingeniero en integración de sistemas eléctricos y mecánicos para la industria.',
                'acreditada': False,
                'virtual': False,
            },
            {
                'nombre': 'Interpretación y Traducción Lengua de Señas – Español',
                'nivel': 'Profesional',
                'duracion': '8 semestres',
                'perfil_profesional': 'Profesional intérprete y traductor entre lengua de señas colombiana y español.',
                'acreditada': False,
                'virtual': False,
            },
        ]

        for prog in programas_ingenieria:
            try:
                ProgramaService.crear_programa(
                    db,
                    nombre=prog['nombre'],
                    nivel=prog['nivel'],
                    facultad_id=facultad_ingenieria.id,
                    duracion=prog['duracion'],
                    perfil_profesional=prog['perfil_profesional'],
                    acreditada=prog['acreditada'],
                    virtual=prog['virtual'],
                )
                print(f"    {prog['nombre']} ({prog['nivel']})")
            except Exception as e:
                print(f"    {prog['nombre']}: {str(e)}")

        # ====== ESTUDIANTES DE EJEMPLO ======
        print("\nCREANDO ESTUDIANTES DE EJEMPLO")
        print("-" * 80)

        from src.models.base import Carrera
        carreras = db.query(Carrera).limit(3).all()

        if not carreras:
            print("  No hay carreras disponibles para asignar a estudiantes.")
        else:
            estudiantes_data = [
                {
                    'documento': '1001234567',
                    'nombre': 'Juan',
                    'apellido': 'García',
                    'email': 'juan.garcia@itm.edu.co',
                    'telefono': '3001234567',
                    'genero': 'Masculino',
                    'carrera': carreras[0],
                    'estado': 'Disponible',
                },
                {
                    'documento': '1002345678',
                    'nombre': 'María',
                    'apellido': 'López',
                    'email': 'maria.lopez@itm.edu.co',
                    'telefono': '3012345678',
                    'genero': 'Femenino',
                    'carrera': carreras[1] if len(carreras) > 1 else carreras[0],
                    'estado': 'Disponible',
                },
                {
                    'documento': '1003456789',
                    'nombre': 'Carlos',
                    'apellido': 'Rodríguez',
                    'email': 'carlos.rodriguez@itm.edu.co',
                    'telefono': '3023456789',
                    'genero': 'No Binario',
                    'carrera': carreras[2] if len(carreras) > 2 else carreras[0],
                    'estado': 'Contratado',
                },
            ]

            for est_data in estudiantes_data:
                try:
                    carrera = est_data['carrera']
                    est = EstudianteService.crear_estudiante(
                        db,
                        numero_documento=est_data['documento'],
                        nombre=est_data['nombre'],
                        apellido=est_data['apellido'],
                        email=est_data['email'],
                        telefono=est_data['telefono'],
                        genero=est_data['genero'],
                        carrera_id=carrera.id,
                        facultad_id=carrera.facultad_id,
                    )

                    if est_data['estado'] != 'Disponible':
                        EstudianteService.actualizar_estado_practica(
                            db, est.id, est_data['estado']
                        )

                    print(f"  {est_data['nombre']} {est_data['apellido']} ({est_data['estado']})")
                except Exception as e:
                    print(f"  {est_data['nombre']} {est_data['apellido']}: {str(e)}")

        total_programas = (
            len(programas_artes) + len(programas_admin) +
            len(programas_exactas) + len(programas_ingenieria)
        )

        print("\n" + "=" * 80)
        print("BASE DE DATOS POBLADA EXITOSAMENTE")
        print("=" * 80)
        print("\nRESUMEN:")
        print(f"  Facultades: 4")
        print(f"  Programas: {total_programas}")
        print(f"  Estudiantes de ejemplo: 3")
        print("\nLa aplicacion esta lista para usar!")
        print("   Accede a: http://localhost:5000")

    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == '__main__':
    from src.database.init_db import init_database
    print("Inicializando base de datos...")
    init_database()
    print("Base de datos inicializada\n")

    populate_database()
