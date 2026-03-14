"""
Script de inicialización de la base de datos
"""
from sqlalchemy import text
from src.models.base import Base
from src.database.connection import engine
from src.config import get_config

def create_database():
    """
    Crea la base de datos si no existe
    """
    config = get_config()
    
    # Obtener credenciales
    db_user = config.DB_USER
    db_password = config.DB_PASSWORD
    db_host = config.DB_HOST
    db_port = config.DB_PORT
    db_name = config.DB_NAME
    
    # Conectar a postgres por defecto
    postgres_uri = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/postgres"
    
    try:
        from sqlalchemy import create_engine as create_temp_engine
        temp_engine = create_temp_engine(postgres_uri)
        
        with temp_engine.connect() as conn:
            # Autocommit para CREATE DATABASE
            conn = conn.connection
            conn.set_isolation_level(0)
            
            # Verificar si la base de datos existe
            cursor = conn.cursor()
            cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
            exists = cursor.fetchone()
            
            if not exists:
                print(f"Creando base de datos: {db_name}")
                cursor.execute(f"CREATE DATABASE {db_name}")
                print(f"Base de datos {db_name} creada exitosamente")
            else:
                print(f"Base de datos {db_name} ya existe")
            
            cursor.close()
            conn.set_isolation_level(1)
        
        temp_engine.dispose()
    except Exception as e:
        print(f"Error al crear la base de datos: {e}")
        print("Asegúrate de que PostgreSQL está ejecutándose y las credenciales son correctas")
        return False
    
    return True

def _seed_data(session):
    """Inserta facultades y programas del ITM si la BD está vacía."""
    from src.models.base import Facultad, Carrera

    FACULTADES = [
        {
            'nombre': 'Facultad de Artes y Humanidades',
            'descripcion': 'Campus La Floresta - Programas en artes, cine, música y diseño',
            'programas': [
                ('Artes Visuales', 'Profesional', '9 semestres', False, False),
                ('Cine', 'Profesional', '9 semestres', False, False),
                ('Artes de la Grabación y Producción Musical', 'Profesional', '10 semestres', False, False),
                ('Tecnología en Informática Musical', 'Tecnología', '6 semestres', False, False),
                ('Tecnología en Diseño Industrial', 'Tecnología', '6 semestres', False, False),
                ('Ingeniería en Diseño Industrial', 'Ingeniería', '10 semestres', False, False),
            ],
        },
        {
            'nombre': 'Facultad de Ciencias Económicas y Administrativas',
            'descripcion': 'Campus Fraternidad - Programas en administración, finanzas y negocios',
            'programas': [
                ('Tecnología en Gestión Administrativa', 'Tecnología', '6 semestres', False, False),
                ('Tecnología en Análisis de Costos y Presupuestos', 'Tecnología', '6 semestres', False, False),
                ('Tecnología en Calidad', 'Tecnología', '6 semestres', False, False),
                ('Tecnología en Producción', 'Tecnología', '6 semestres', False, False),
                ('Administración Tecnológica', 'Profesional', '10 semestres', True, False),
                ('Administración del Deporte', 'Profesional', '9 semestres', False, False),
                ('Ingeniería Financiera y de Negocios', 'Ingeniería', '10 semestres', True, False),
                ('Ingeniería de Producción', 'Ingeniería', '10 semestres', True, False),
                ('Ingeniería de la Calidad', 'Ingeniería', '10 semestres', False, False),
            ],
        },
        {
            'nombre': 'Facultad de Ciencias Exactas y Aplicadas',
            'descripcion': 'Campus Robledo - Programas en ciencias, salud y ambiente',
            'programas': [
                ('Tecnología en Mantenimiento de Equipo Biomédico', 'Tecnología', '6 semestres', False, False),
                ('Tecnología en Construcción de Acabados Arquitectónicos', 'Tecnología', '6 semestres', False, False),
                ('Ingeniería Biomédica', 'Ingeniería', '10 semestres', True, False),
                ('Ciencias Ambientales', 'Profesional', '9 semestres', False, False),
                ('Ciencia y Tecnología de los Alimentos', 'Profesional', '10 semestres', False, False),
                ('Física', 'Profesional', '10 semestres', False, False),
                ('Química Industrial', 'Profesional', '10 semestres', False, False),
            ],
        },
        {
            'nombre': 'Facultad de Ingenierías',
            'descripcion': 'Campus Robledo - Programas en ingeniería, tecnología e informática',
            'programas': [
                ('Tecnología en Sistemas de Información', 'Tecnología', '6 semestres', False, False),
                ('Tecnología en Telecomunicaciones', 'Tecnología', '6 semestres', False, False),
                ('Tecnología en Electrónica', 'Tecnología', '6 semestres', False, False),
                ('Tecnología en Sistemas Electromecánicos', 'Tecnología', '6 semestres', False, False),
                ('Tecnología en Sistemas de Producción', 'Tecnología', '6 semestres', False, False),
                ('Ingeniería de Sistemas', 'Ingeniería', '10 semestres', True, False),
                ('Ingeniería de Telecomunicaciones', 'Ingeniería', '10 semestres', True, False),
                ('Ingeniería Electrónica', 'Ingeniería', '10 semestres', True, False),
                ('Ingeniería Electromecánica', 'Ingeniería', '10 semestres', False, False),
                ('Interpretación y Traducción Lengua de Señas – Español', 'Profesional', '8 semestres', False, False),
            ],
        },
    ]

    total_programas = 0
    for f_data in FACULTADES:
        facultad = Facultad(nombre=f_data['nombre'], descripcion=f_data['descripcion'])
        session.add(facultad)
        session.flush()  # obtener facultad.id

        for nombre, nivel, duracion, acreditada, virtual in f_data['programas']:
            carrera = Carrera(
                nombre=nombre,
                nivel=nivel,
                duracion=duracion,
                acreditada=acreditada,
                virtual=virtual,
                facultad_id=facultad.id,
            )
            session.add(carrera)
            total_programas += 1

    session.commit()
    print(f"✓ Datos iniciales insertados: 4 facultades, {total_programas} programas")


def _migrate_cv_columns():
    """Agrega columnas de CV a estudiantes si no existen (migración idempotente)."""
    cv_columns = [
        ("cv_s3_key", "VARCHAR(500)"),
        ("cv_filename", "VARCHAR(255)"),
        ("cv_upload_date", "TIMESTAMP"),
    ]
    try:
        with engine.connect() as conn:
            for col_name, col_type in cv_columns:
                result = conn.execute(text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name='estudiantes' AND column_name=:col"
                ), {"col": col_name})
                if not result.fetchone():
                    conn.execute(text(
                        f"ALTER TABLE estudiantes ADD COLUMN {col_name} {col_type}"
                    ))
                    conn.commit()
                    print(f"✓ Columna '{col_name}' agregada a estudiantes")
    except Exception as e:
        print(f"Advertencia en migración CV: {e}")


def init_database():
    """
    Inicializa todas las tablas y siembra datos si la BD está vacía.
    Es idempotente: se puede llamar en cada arranque sin efectos secundarios.
    """
    print("Inicializando estructura de base de datos...")

    try:
        # Crear todas las tablas (no hace nada si ya existen)
        Base.metadata.create_all(bind=engine)
        print("✓ Tablas creadas exitosamente")

        # Migración: columnas de CV para bases de datos existentes
        _migrate_cv_columns()

        from sqlalchemy.orm import sessionmaker
        from src.models.base import Facultad
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            if session.query(Facultad).count() == 0:
                print("Base de datos vacía, insertando datos iniciales...")
                _seed_data(session)
            else:
                print("✓ Datos ya presentes, omitiendo seed")
        except Exception as e:
            session.rollback()
            print(f"Error al insertar datos iniciales: {e}")
        finally:
            session.close()

        return True
    except Exception as e:
        print(f"✗ Error al inicializar la base de datos: {e}")
        return False

def main():
    """
    Función principal para inicializar todo
    """
    print("=" * 60)
    print("INICIALIZADOR DE BASE DE DATOS - Practicas ITM")
    print("=" * 60)
    
    # Paso 1: Crear base de datos
    if not create_database():
        print("\n✗ Inicialización abortada")
        return
    
    # Paso 2: Inicializar tablas
    if not init_database():
        print("\n✗ Inicialización abortada")
        return
    
    print("\n" + "=" * 60)
    print("✓ Base de datos inicializada correctamente")
    print("=" * 60)

if __name__ == "__main__":
    main()
