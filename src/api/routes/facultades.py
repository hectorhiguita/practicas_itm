"""
Rutas de la API para gestionar facultades
"""
from flask import Blueprint, request, jsonify
from src.database.connection import get_session
from src.services.facultad_service import FacultadService

bp = Blueprint('facultades', __name__, url_prefix='/api/facultades')

# Funciones auxiliares
def respuesta_error(mensaje: str, codigo: int = 400):
    """Crea una respuesta de error"""
    return jsonify({'error': mensaje}), codigo

def respuesta_exito(datos=None, mensaje: str = None, codigo: int = 200):
    """Crea una respuesta exitosa"""
    respuesta = {}
    if mensaje:
        respuesta['mensaje'] = mensaje
    if datos is not None:
        respuesta['datos'] = datos
    return jsonify(respuesta), codigo

# CRUD de Facultades
@bp.route('/', methods=['GET'])
def listar_facultades():
    """Lista todas las facultades"""
    try:
        db = get_session()
        facultades = FacultadService.obtener_todas_facultades(db)
        db.close()
        
        datos = [f.to_dict() for f in facultades]
        return respuesta_exito(datos, f"Se encontraron {len(datos)} facultades")
    
    except Exception as e:
        return respuesta_error(f"Error al listar facultades: {str(e)}", 500)

@bp.route('/', methods=['POST'])
def crear_facultad():
    """
    Crea una nueva facultad
    Body JSON requerido:
        - nombre: str (único)
        - descripcion: str (opcional)
    """
    try:
        datos = request.get_json()
        if not datos or 'nombre' not in datos:
            return respuesta_error("Campo 'nombre' requerido en JSON")
        
        db = get_session()
        
        nueva_facultad = FacultadService.crear_facultad(
            db=db,
            nombre=datos['nombre'],
            descripcion=datos.get('descripcion')
        )
        
        db.close()
        return respuesta_exito(nueva_facultad.to_dict(), 
                             "Facultad creada exitosamente", 201)
    
    except ValueError as e:
        return respuesta_error(str(e), 400)
    except Exception as e:
        return respuesta_error(f"Error al crear facultad: {str(e)}", 500)

@bp.route('/<int:facultad_id>', methods=['GET'])
def obtener_facultad(facultad_id):
    """Obtiene una facultad por ID"""
    try:
        db = get_session()
        facultad = FacultadService.obtener_facultad(db, facultad_id)
        db.close()
        
        if not facultad:
            return respuesta_error("Facultad no encontrada", 404)
        
        return respuesta_exito(facultad.to_dict())
    
    except Exception as e:
        return respuesta_error(f"Error al obtener facultad: {str(e)}", 500)

@bp.route('/<int:facultad_id>', methods=['PUT'])
def actualizar_facultad(facultad_id):
    """
    Actualiza una facultad
    Body JSON (todos los campos opcionales):
        - nombre: str
        - descripcion: str
    """
    try:
        datos = request.get_json()
        if not datos:
            return respuesta_error("Body JSON requerido")
        
        db = get_session()
        
        facultad_actualizada = FacultadService.actualizar_facultad(
            db=db,
            facultad_id=facultad_id,
            nombre=datos.get('nombre'),
            descripcion=datos.get('descripcion')
        )
        
        if not facultad_actualizada:
            db.close()
            return respuesta_error("Facultad no encontrada", 404)
        
        db.close()
        return respuesta_exito(facultad_actualizada.to_dict(), 
                             "Facultad actualizada exitosamente")
    
    except Exception as e:
        return respuesta_error(f"Error al actualizar facultad: {str(e)}", 500)

@bp.route('/<int:facultad_id>', methods=['DELETE'])
def eliminar_facultad(facultad_id):
    """Elimina una facultad"""
    try:
        db = get_session()
        
        if not FacultadService.eliminar_facultad(db, facultad_id):
            db.close()
            return respuesta_error("Facultad no encontrada", 404)
        
        db.close()
        return respuesta_exito(None, "Facultad eliminada exitosamente")
    
    except Exception as e:
        return respuesta_error(f"Error al eliminar facultad: {str(e)}", 500)
