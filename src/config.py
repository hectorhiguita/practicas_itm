"""
Configuración centralizada de la aplicación
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración base"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Auth - Credenciales locales (usar hash bcrypt en producción)
    # Generar hash: python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('tu_password'))"
    ADMIN_USER = os.getenv('ADMIN_USER', 'admin')
    ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH', '')
    
    # Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'practicas_itm')
    DB_USER = os.getenv('DB_USER', 'practicas_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'
    
    # App
    APP_HOST = os.getenv('APP_HOST', '0.0.0.0')
    APP_PORT = int(os.getenv('APP_PORT', 5000))

    # EFS - Almacenamiento de CVs
    EFS_CV_PATH = os.getenv('EFS_CV_PATH', '/mnt/efs/cvs')
    CV_MAX_SIZE_MB = int(os.getenv('CV_MAX_SIZE_MB', '5'))

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    DISABLE_AUTH = True  # Desactiva el guard de autenticación en tests
    DB_NAME = 'practicas_itm_test'
    SQLALCHEMY_DATABASE_URI = f"postgresql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/practicas_itm_test"

# Seleccionar configuración según entorno
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Obtiene la configuración según el entorno"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
