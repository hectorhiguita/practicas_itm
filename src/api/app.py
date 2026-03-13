"""
Aplicación Flask - Punto de entrada principal para la API
"""
from flask import Flask, jsonify
from src.config import get_config
from src.api.routes import estudiantes, facultades, carreras
from src.database.connection import test_connection

def create_app(config=None):
    """
    Factory function para crear la aplicación Flask
    
    Args:
        config: Configuración personalizada (opcional)
        
    Returns:
        Flask: Aplicación Flask configurada
    """
    app = Flask(__name__)
    
    # Cargar configuración
    if config:
        app.config.from_object(config)
    else:
        app.config.from_object(get_config())
    
    # Registrar blueprints
    app.register_blueprint(estudiantes.bp)
    app.register_blueprint(facultades.bp)
    app.register_blueprint(carreras.bp)
    
    # Ruta de prueba
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Verifica el estado de la aplicación"""
        db_status = test_connection()
        return jsonify({
            'status': 'healthy' if db_status else 'unhealthy',
            'database': 'connected' if db_status else 'disconnected'
        }), 200 if db_status else 503
    
    # Ruta raíz
    @app.route('/', methods=['GET'])
    def index():
        """Página de inicio de la API"""
        return jsonify({
            'nombre': 'Practicas ITM - API',
            'version': '1.0.0',
            'descripcion': 'Sistema de gestión de prácticas universitarias',
            'endpoints': {
                'health': '/api/health',
                'estudiantes': '/api/estudiantes',
                'facultades': '/api/facultades',
                'carreras': '/api/carreras'
            }
        }), 200
    
    # Manejador de errores 404
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint no encontrado'}), 404
    
    # Manejador de errores 500
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Error interno del servidor'}), 500
    
    return app

# Crear la aplicación
app = create_app()

if __name__ == '__main__':
    config = get_config()
    app.run(
        host=config.APP_HOST,
        port=config.APP_PORT,
        debug=config.FLASK_DEBUG
    )
