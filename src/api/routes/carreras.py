"""
Rutas de la API para gestionar carreras
"""
from flask import Blueprint, request, jsonify
from src.database.connection import get_session
from src.services.carrera_service import CarreraService

bp = Blueprint('carreras', __name__, url_prefix='/api/carreras')


def respuesta_error(mensaje: str, codigo: int = 400):
    return jsonify({'error': mensaje}), codigo


def respuesta_exito(datos=None, mensaje: str = None, codigo: int = 200):
    respuesta = {}
    if mensaje:
        respuesta['mensaje'] = mensaje
    if datos is not None:
        respuesta['datos'] = datos
    return jsonify(respuesta), codigo


@bp.route('/', methods=['GET'])
def listar_carreras():
    """Lista todas las carreras. Parámetro opcional: facultad_id"""
    db = get_session()
    try:
        facultad_id = request.args.get('facultad_id', type=int)
        if facultad_id:
            carreras = CarreraService.obtener_carreras_por_facultad(db, facultad_id)
        else:
            carreras = CarreraService.obtener_todas_carreras(db)

        datos = [c.to_dict() for c in carreras]
        return respuesta_exito(datos, f"Se encontraron {len(datos)} carreras")

    except Exception as e:
        return respuesta_error(f"Error al listar carreras: {str(e)}", 500)
    finally:
        db.close()


@bp.route('/', methods=['POST'])
def crear_carrera():
    """
    Crea una nueva carrera.
    Body JSON requerido: nombre, facultad_id.
    Opcionales: descripcion, nivel, duracion, perfil_profesional, acreditada, virtual.
    """
    db = get_session()
    try:
        datos = request.get_json()
        if not datos:
            return respuesta_error("Body JSON requerido")

        for campo in ('nombre', 'facultad_id'):
            if campo not in datos:
                return respuesta_error(f"Campo requerido faltante: {campo}")

        nueva_carrera = CarreraService.crear_carrera(
            db=db,
            nombre=datos['nombre'],
            facultad_id=datos['facultad_id'],
            descripcion=datos.get('descripcion'),
            nivel=datos.get('nivel', 'Tecnología'),
            duracion=datos.get('duracion'),
            perfil_profesional=datos.get('perfil_profesional'),
            acreditada=datos.get('acreditada', False),
            virtual=datos.get('virtual', False),
        )

        resultado = nueva_carrera.to_dict()
        return respuesta_exito(resultado, "Carrera creada exitosamente", 201)

    except ValueError as e:
        return respuesta_error(str(e), 400)
    except Exception as e:
        return respuesta_error(f"Error al crear carrera: {str(e)}", 500)
    finally:
        db.close()


@bp.route('/<int:carrera_id>', methods=['GET'])
def obtener_carrera(carrera_id):
    """Obtiene una carrera por ID"""
    db = get_session()
    try:
        carrera = CarreraService.obtener_carrera(db, carrera_id)
        if not carrera:
            return respuesta_error("Carrera no encontrada", 404)

        return respuesta_exito(carrera.to_dict())

    except Exception as e:
        return respuesta_error(f"Error al obtener carrera: {str(e)}", 500)
    finally:
        db.close()


@bp.route('/<int:carrera_id>', methods=['PUT'])
def actualizar_carrera(carrera_id):
    """Actualiza una carrera. Body JSON con campos opcionales: nombre, descripcion."""
    db = get_session()
    try:
        datos = request.get_json()
        if not datos:
            return respuesta_error("Body JSON requerido")

        carrera_actualizada = CarreraService.actualizar_carrera(
            db=db,
            carrera_id=carrera_id,
            nombre=datos.get('nombre'),
            descripcion=datos.get('descripcion'),
        )

        if not carrera_actualizada:
            return respuesta_error("Carrera no encontrada", 404)

        return respuesta_exito(carrera_actualizada.to_dict(), "Carrera actualizada exitosamente")

    except Exception as e:
        return respuesta_error(f"Error al actualizar carrera: {str(e)}", 500)
    finally:
        db.close()


@bp.route('/<int:carrera_id>', methods=['DELETE'])
def eliminar_carrera(carrera_id):
    """Elimina una carrera"""
    db = get_session()
    try:
        if not CarreraService.eliminar_carrera(db, carrera_id):
            return respuesta_error("Carrera no encontrada", 404)

        return respuesta_exito(None, "Carrera eliminada exitosamente")

    except Exception as e:
        return respuesta_error(f"Error al eliminar carrera: {str(e)}", 500)
    finally:
        db.close()
