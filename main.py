"""
Punto de entrada principal de la aplicación
"""
import os
import sys

# Agregar el directorio actual al path de Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.api.app import app, create_app
from src.config import get_config

if __name__ == '__main__':
    config = get_config()
    
    print("=" * 60)
    print("Practicas ITM - Sistema de Gestión de Prácticas")
    print("=" * 60)
    print(f"Ambiente: {config.FLASK_ENV}")
    print(f"Debug: {config.FLASK_DEBUG}")
    print(f"Host: {config.APP_HOST}")
    print(f"Puerto: {config.APP_PORT}")
    print(f"Base de datos: {config.DB_NAME}")
    print("=" * 60)
    print("Iniciando servidor...")
    print("=" * 60)
    
    app.run(
        host=config.APP_HOST,
        port=config.APP_PORT,
        debug=config.FLASK_DEBUG
    )
