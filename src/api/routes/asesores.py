"""
Rutas de la API para gestionar Asesores de Prácticas
"""
from flask import Blueprint, request, jsonify
from src.database.connection import get_session
from src.services.asesor_service import AsesorService
from src.services.email_service import send_credentials_email

asesores_bp = Blueprint('asesores', __name__, url_prefix='/api/asesores')


def _ok(datos=None, mensaje=None, codigo=200):
    resp = {}
    if mensaje:
        resp['mensaje'] = mensaje
    if datos is not None:
        resp['datos'] = datos
    return jsonify(resp), codigo


def _err(mensaje, codigo=400):
    return jsonify({'error': mensaje}), codigo


# ── CRUD Asesores ─────────────────────────────────────────────────────────────

@asesores_bp.route('/', methods=['GET'])
def listar_asesores():
    """Lista todos los asesores con sus estadísticas de estudiantes."""
    solo_activos = request.args.get('activos', 'false').lower() == 'true'
    db = get_session()
    try:
        dashboard = AsesorService.get_dashboard(db)
        if solo_activos:
            dashboard = [a for a in dashboard if a['activo']]
        return _ok(dashboard)
    finally:
        db.close()


@asesores_bp.route('/<int:asesor_id>', methods=['GET'])
def obtener_asesor(asesor_id):
    db = get_session()
    try:
        asesor = AsesorService.obtener_asesor(db, asesor_id)
        if not asesor:
            return _err('Asesor no encontrado', 404)
        datos = asesor.to_dict()
        datos['estadisticas'] = AsesorService.get_estadisticas(db, asesor_id)
        return _ok(datos)
    finally:
        db.close()


@asesores_bp.route('/', methods=['POST'])
def crear_asesor():
    datos = request.get_json(silent=True) or {}
    if not datos.get('nombre') or not datos.get('apellido') or not datos.get('email'):
        return _err('nombre, apellido y email son requeridos')
    db = get_session()
    try:
        asesor, plain_pw = AsesorService.crear_asesor(db, datos)
        # Enviar credenciales por correo (no bloqueante ante fallo de email)
        email_ok = send_credentials_email(
            to_email=asesor.email,
            nombre=f"{asesor.nombre} {asesor.apellido}",
            username=asesor.username,
            password=plain_pw,
        )
        respuesta = asesor.to_dict()
        respuesta['username'] = asesor.username
        respuesta['password_temporal'] = plain_pw   # mostrado una sola vez en pantalla
        respuesta['email_enviado'] = email_ok
        return _ok(respuesta, 'Asesor creado exitosamente', 201)
    except Exception as e:
        return _err(f'Error al crear asesor: {str(e)}', 500)
    finally:
        db.close()


@asesores_bp.route('/<int:asesor_id>', methods=['PUT'])
def actualizar_asesor(asesor_id):
    datos = request.get_json(silent=True) or {}
    db = get_session()
    try:
        asesor = AsesorService.actualizar_asesor(db, asesor_id, datos)
        if not asesor:
            return _err('Asesor no encontrado', 404)
        return _ok(asesor.to_dict(), 'Asesor actualizado')
    except Exception as e:
        return _err(f'Error al actualizar asesor: {str(e)}', 500)
    finally:
        db.close()


@asesores_bp.route('/<int:asesor_id>', methods=['DELETE'])
def eliminar_asesor(asesor_id):
    db = get_session()
    try:
        ok = AsesorService.eliminar_asesor(db, asesor_id)
        if not ok:
            return _err('Asesor no encontrado', 404)
        return _ok(mensaje='Asesor desactivado')
    finally:
        db.close()


# ── Estudiantes del asesor ────────────────────────────────────────────────────

@asesores_bp.route('/<int:asesor_id>/estudiantes', methods=['GET'])
def estudiantes_asesor(asesor_id):
    """Lista los estudiantes de un asesor (activos + histórico)."""
    incluir_finalizados = request.args.get('finalizados', 'true').lower() == 'true'
    db = get_session()
    try:
        asesor = AsesorService.obtener_asesor(db, asesor_id)
        if not asesor:
            return _err('Asesor no encontrado', 404)
        estudiantes = AsesorService.get_estudiantes_asesor(db, asesor_id, incluir_finalizados)
        return _ok([e.to_dict() for e in estudiantes])
    finally:
        db.close()


@asesores_bp.route('/asignar', methods=['POST'])
def asignar_asesor():
    """Asigna un asesor a un estudiante. Body: {estudiante_id, asesor_id}"""
    datos = request.get_json(silent=True) or {}
    estudiante_id = datos.get('estudiante_id')
    asesor_id = datos.get('asesor_id')  # None para desasignar

    if not estudiante_id:
        return _err('estudiante_id es requerido')
    db = get_session()
    try:
        estudiante = AsesorService.asignar_asesor(db, estudiante_id, asesor_id)
        if not estudiante:
            return _err('Estudiante o asesor no encontrado', 404)
        return _ok(estudiante.to_dict(), 'Asesor asignado correctamente')
    except Exception as e:
        return _err(f'Error al asignar asesor: {str(e)}', 500)
    finally:
        db.close()
