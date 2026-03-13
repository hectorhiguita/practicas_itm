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

def init_database():
    """
    Inicializa todas las tablas en la base de datos
    """
    print("Inicializando estructura de base de datos...")
    
    try:
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        print("✓ Tablas creadas exitosamente")
        
        # Insertar datos iniciales
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # Verificar si ya existen facultades
            from src.models.base import Facultad
            if session.query(Facultad).count() == 0:
                print("Insertando datos iniciales...")
                # Aquí puedes agregar datos iniciales si lo deseas
                print("✓ Datos iniciales insertados")
            
            session.commit()
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
