"""
Rutas API para gestionar Programas Académicos
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import and_, or_
from src.database.connection import get_session
from src.models.base import Carrera
from src.services.programa_service import ProgramaService

programas_bp = Blueprint('programas', __name__, url_prefix='/api/programas')

@programas_bp.route('', methods=['GET'])
def obtener_programas():
    """
    Obtiene todos los programas académicos
    Query params:
        - facultad_id: Filtrar por facultad (opcional)
        - nivel: Filtrar por nivel (opcional)
        - acreditados: true/false para filtrar acreditados (opcional)
        - virtuales: true/false para filtrar virtuales (opcional)
    """
    db = get_session()
    try:
        facultad_id = request.args.get('facultad_id', type=int)
        nivel = request.args.get('nivel', type=str)
        acreditados = request.args.get('acreditados', type=lambda x: x.lower() == 'true')
        virtuales = request.args.get('virtuales', type=lambda x: x.lower() == 'true')
        
        # Obtener base
        query = db.query(Carrera)
        
        # Aplicar filtros
        if facultad_id:
            query = query.filter(Carrera.facultad_id == facultad_id)
        
        if nivel:
            query = query.filter(Carrera.nivel == nivel)
        
        if acreditados:
            query = query.filter(Carrera.acreditada == 1)
        
        if virtuales:
            query = query.filter(Carrera.virtual == 1)
        
        programas = query.order_by(Carrera.nombre).all()
        
        return jsonify({
            'success': True,
            'total': len(programas),
            'data': [p.to_dict() for p in programas]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@programas_bp.route('/<int:programa_id>', methods=['GET'])
def obtener_programa(programa_id):
    """
    Obtiene un programa académico específico
    """
    db = get_session()
    try:
        programa = ProgramaService.obtener_programa_por_id(db, programa_id)
        
        if not programa:
            return jsonify({
                'success': False,
                'error': 'Programa no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'data': programa.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@programas_bp.route('/por-nivel/<string:nivel>', methods=['GET'])
def obtener_por_nivel(nivel):
    """
    Obtiene programas filtrados por nivel
    """
    db = get_session()
    try:
        programas = ProgramaService.obtener_programas_por_nivel(db, nivel)
        
        return jsonify({
            'success': True,
            'total': len(programas),
            'nivel': nivel,
            'data': [p.to_dict() for p in programas]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@programas_bp.route('/acreditados', methods=['GET'])
def obtener_acreditados():
    """
    Obtiene solo programas acreditados
    """
    db = get_session()
    try:
        programas = ProgramaService.obtener_programas_acreditados(db)
        
        return jsonify({
            'success': True,
            'total': len(programas),
            'data': [p.to_dict() for p in programas]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@programas_bp.route('/virtuales', methods=['GET'])
def obtener_virtuales():
    """
    Obtiene solo programas virtuales
    """
    db = get_session()
    try:
        programas = ProgramaService.obtener_programas_virtuales(db)
        
        return jsonify({
            'success': True,
            'total': len(programas),
            'data': [p.to_dict() for p in programas]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@programas_bp.route('/estadisticas', methods=['GET'])
def obtener_estadisticas():
    """
    Obtiene estadísticas generales de programas
    """
    db = get_session()
    try:
        stats = ProgramaService.obtener_estadisticas_programas(db)
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@programas_bp.route('', methods=['POST'])
def crear_programa():
    """
    Crea un nuevo programa académico
    Body JSON:
        - nombre (str, required)
        - nivel (str, required): Tecnología, Profesional, Ingeniería
        - facultad_id (int, required)
        - duracion (str, optional)
        - perfil_profesional (str, optional)
        - acreditada (bool, optional)
        - virtual (bool, optional)
    """
    db = get_session()
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Body JSON requerido'
            }), 400
        
        # Validar campos requeridos
        if not data.get('nombre') or not data.get('nivel') or not data.get('facultad_id'):
            return jsonify({
                'success': False,
                'error': 'Campos requeridos: nombre, nivel, facultad_id'
            }), 400
        
        programa = ProgramaService.crear_programa(
            db,
            nombre=data['nombre'],
            nivel=data['nivel'],
            facultad_id=data['facultad_id'],
            duracion=data.get('duracion'),
            perfil_profesional=data.get('perfil_profesional'),
            acreditada=data.get('acreditada', False),
            virtual=data.get('virtual', False)
        )
        
        return jsonify({
            'success': True,
            'message': 'Programa creado exitosamente',
            'data': programa.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@programas_bp.route('/<int:programa_id>', methods=['PUT'])
def actualizar_programa(programa_id):
    """
    Actualiza un programa académico
    """
    db = get_session()
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Body JSON requerido'
            }), 400
        
        programa = ProgramaService.actualizar_programa(db, programa_id, **data)
        
        if not programa:
            return jsonify({
                'success': False,
                'error': 'Programa no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Programa actualizado exitosamente',
            'data': programa.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()

@programas_bp.route('/<int:programa_id>', methods=['DELETE'])
def eliminar_programa(programa_id):
    """
    Elimina un programa académico
    """
    db = get_session()
    try:
        if ProgramaService.eliminar_programa(db, programa_id):
            return jsonify({
                'success': True,
                'message': 'Programa eliminado exitosamente'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Programa no encontrado'
            }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        db.close()
