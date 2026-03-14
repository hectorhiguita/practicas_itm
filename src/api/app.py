"""
Aplicación Flask - Punto de entrada principal para la API
"""
from flask import Flask, jsonify, send_from_directory
import os
from src.config import get_config
from src.api.routes import estudiantes, facultades, carreras, programas
from src.api.routes.importar import importar_bp
from src.database.connection import test_connection
from src.database.init_db import init_database

def create_app(config=None):
    """
    Factory function para crear la aplicación Flask
    
    Args:
        config: Configuración personalizada (opcional)
        
    Returns:
        Flask: Aplicación Flask configurada
    """
    # Get the root directory for static and template files
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    
    app = Flask(__name__, 
                static_folder=static_dir,
                static_url_path='/static')
    
    # Cargar configuración
    if config:
        app.config.from_object(config)
    else:
        app.config.from_object(get_config())
    
    # Inicializar BD solo si no está desactivado (en producción lo hace el entrypoint)
    import os
    if not os.environ.get('SKIP_DB_INIT'):
        init_database()

    # Registrar blueprints
    app.register_blueprint(estudiantes.bp)
    app.register_blueprint(facultades.bp)
    app.register_blueprint(carreras.bp)
    app.register_blueprint(programas.programas_bp)
    app.register_blueprint(importar_bp)
    
    # Ruta de prueba
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Verifica el estado de la aplicación"""
        db_status = test_connection()
        return jsonify({
            'status': 'healthy' if db_status else 'unhealthy',
            'database': 'connected' if db_status else 'disconnected'
        }), 200 if db_status else 503
    
    # Ruta raíz - Servir dashboard
    @app.route('/', methods=['GET'])
    def dashboard():
        """Serve the dashboard"""
        try:
            # Read the static/index.html file
            static_path = os.path.join(os.path.dirname(__file__), 'static', 'index.html')
            with open(static_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return jsonify({
                'nombre': 'Practicas ITM - API',
                'version': '1.0.0',
                'descripcion': 'Sistema de gestión de prácticas universitarias',
                'endpoints': {
                    'health': '/api/health',
                    'estudiantes': '/api/estudiantes',
                    'facultades': '/api/facultades',
                    'carreras': '/api/carreras',
                    'programas': '/api/programas'
                }
            }), 200
    
    # Servir archivos estáticos
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        """Serve static files"""
        return send_from_directory(app.static_folder, filename)
    
    # Ruta API info
    @app.route('/api/info', methods=['GET'])
    def api_info():
        """Información de la API"""
        return jsonify({
            'nombre': 'Practicas ITM - API',
            'version': '1.0.0',
            'descripcion': 'Sistema de gestión de prácticas universitarias',
            'endpoints': {
                'health': '/api/health',
                'estudiantes': '/api/estudiantes',
                'facultades': '/api/facultades',
                'carreras': '/api/carreras',
                'programas': '/api/programas'
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
