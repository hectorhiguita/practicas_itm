"""
Rutas de la API para gestionar estudiantes
"""
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from flask_login import current_user
from src.database.connection import get_session
from src.services.estudiante_service import EstudianteService
from src.services.cv_service import CVService
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest

bp = Blueprint('estudiantes', __name__, url_prefix='/api/estudiantes')

# Funciones auxiliares para respuestas
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

# CRUD de Estudiantes
@bp.route('/', methods=['GET'])
def listar_estudiantes():
    """
    Lista todos los estudiantes
    Parámetros opcionales:
        - facultad_id: Filtrar por facultad
        - carrera_id: Filtrar por carrera
        - estado: Filtrar por estado (disponible, contratado, etc)
    """
    try:
        db = get_session()
        facultad_id = request.args.get('facultad_id', type=int)
        carrera_id = request.args.get('carrera_id', type=int)
        estado = request.args.get('estado', type=str)

        # Asesores solo ven sus propios estudiantes
        asesor_filter = None
        if hasattr(current_user, 'role') and current_user.role == 'asesor':
            asesor_filter = current_user.asesor_id

        if facultad_id:
            estudiantes = EstudianteService.obtener_estudiantes_por_facultad(db, facultad_id, asesor_id=asesor_filter)
        elif carrera_id:
            estudiantes = EstudianteService.obtener_estudiantes_por_carrera(db, carrera_id, asesor_id=asesor_filter)
        elif estado:
            estudiantes = EstudianteService.obtener_estudiantes_por_estado(db, estado, asesor_id=asesor_filter)
        else:
            estudiantes = EstudianteService.obtener_todos_estudiantes(db, asesor_id=asesor_filter)
        
        db.close()
        datos = [e.to_dict() for e in estudiantes]
        return respuesta_exito(datos, f"Se encontraron {len(datos)} estudiantes")
    
    except ValueError as e:
        return respuesta_error(str(e), 400)
    except Exception as e:
        return respuesta_error(f"Error al listar estudiantes: {str(e)}", 500)

@bp.route('/', methods=['POST'])
def crear_estudiante():
    """
    Crea un nuevo estudiante
    Body JSON requerido:
        - numero_documento: str (único)
        - nombre: str
        - apellido: str
        - email: str (único)
        - genero: str (Masculino, Femenino, Otro)
        - facultad_id: int
        - carrera_id: int
        - telefono: str (opcional)
    """
    try:
        datos = request.get_json()
        if not datos:
            return respuesta_error("Body JSON requerido")
        
        # Validar campos requeridos
        campos_requeridos = ['numero_documento', 'nombre', 'apellido', 'email', 
                            'genero', 'facultad_id', 'carrera_id']
        for campo in campos_requeridos:
            if campo not in datos:
                return respuesta_error(f"Campo requerido faltante: {campo}")
        
        db = get_session()
        
        nuevo_estudiante = EstudianteService.crear_estudiante(
            db=db,
            numero_documento=datos['numero_documento'],
            nombre=datos['nombre'],
            apellido=datos['apellido'],
            email=datos['email'],
            genero=datos['genero'],
            facultad_id=datos['facultad_id'],
            carrera_id=datos['carrera_id'],
            telefono=datos.get('telefono')
        )
        
        db.close()
        return respuesta_exito(nuevo_estudiante.to_dict(), 
                             "Estudiante creado exitosamente", 201)
    
    except ValueError as e:
        return respuesta_error(str(e), 400)
    except IntegrityError as e:
        return respuesta_error("Error de integridad en los datos", 400)
    except Exception as e:
        return respuesta_error(f"Error al crear estudiante: {str(e)}", 500)

@bp.route('/<int:estudiante_id>', methods=['GET'])
def obtener_estudiante(estudiante_id):
    """Obtiene un estudiante por ID"""
    try:
        db = get_session()
        estudiante = EstudianteService.obtener_estudiante(db, estudiante_id)
        db.close()
        
        if not estudiante:
            return respuesta_error("Estudiante no encontrado", 404)
        
        return respuesta_exito(estudiante.to_dict())
    
    except Exception as e:
        return respuesta_error(f"Error al obtener estudiante: {str(e)}", 500)

@bp.route('/<int:estudiante_id>', methods=['PUT'])
def actualizar_estudiante(estudiante_id):
    """
    Actualiza un estudiante
    Body JSON (todos los campos opcionales):
        - nombre: str
        - apellido: str
        - email: str
        - telefono: str
    """
    try:
        datos = request.get_json()
        if not datos:
            return respuesta_error("Body JSON requerido")
        
        db = get_session()
        
        estudiante_actualizado = EstudianteService.actualizar_estudiante(
            db=db,
            estudiante_id=estudiante_id,
            nombre=datos.get('nombre'),
            apellido=datos.get('apellido'),
            email=datos.get('email'),
            telefono=datos.get('telefono'),
            genero=datos.get('genero'),
            facultad_id=datos.get('facultad_id'),
            carrera_id=datos.get('carrera_id'),
            estado_practica=datos.get('estado_practica'),
            tiene_discapacidad=datos.get('tiene_discapacidad'),
            discapacidad_personalizada=datos.get('discapacidad_personalizada'),
            fecha_inicio_contrato=datos.get('fecha_inicio_contrato'),
            fecha_fin_contrato=datos.get('fecha_fin_contrato'),
        )

        if not estudiante_actualizado:
            db.close()
            return respuesta_error("Estudiante no encontrado", 404)

        db.close()
        return respuesta_exito(estudiante_actualizado.to_dict(),
                               "Estudiante actualizado exitosamente")

    except ValueError as e:
        return respuesta_error(str(e), 400)
    except Exception as e:
        return respuesta_error(f"Error al actualizar estudiante: {str(e)}", 500)

@bp.route('/<int:estudiante_id>/estado', methods=['PUT'])
def actualizar_estado_practica(estudiante_id):
    """
    Actualiza el estado de práctica de un estudiante
    Body JSON requerido:
        - estado: str (Disponible, Contratado, Por Finalizar, Finalizó)
    """
    try:
        datos = request.get_json()
        if not datos or 'estado' not in datos:
            return respuesta_error("Campo 'estado' requerido en JSON")
        
        db = get_session()
        
        estudiante_actualizado = EstudianteService.actualizar_estado_practica(
            db=db,
            estudiante_id=estudiante_id,
            nuevo_estado=datos['estado'],
            fecha_inicio_contrato=datos.get('fecha_inicio_contrato'),
            fecha_fin_contrato=datos.get('fecha_fin_contrato'),
        )
        
        if not estudiante_actualizado:
            db.close()
            return respuesta_error("Estudiante no encontrado", 404)
        
        db.close()
        return respuesta_exito(estudiante_actualizado.to_dict(), 
                             "Estado de práctica actualizado exitosamente")
    
    except ValueError as e:
        return respuesta_error(str(e), 400)
    except Exception as e:
        return respuesta_error(f"Error al actualizar estado: {str(e)}", 500)

@bp.route('/<int:estudiante_id>', methods=['DELETE'])
def eliminar_estudiante(estudiante_id):
    """Elimina un estudiante"""
    try:
        db = get_session()
        
        if not EstudianteService.eliminar_estudiante(db, estudiante_id):
            db.close()
            return respuesta_error("Estudiante no encontrado", 404)
        
        db.close()
        return respuesta_exito(None, "Estudiante eliminado exitosamente")
    
    except Exception as e:
        return respuesta_error(f"Error al eliminar estudiante: {str(e)}", 500)

# Revisión automática de estados por vencimiento
@bp.route('/revisar-estados', methods=['POST'])
def revisar_estados():
    """Cambia a 'Por Finalizar' los estudiantes cuyo contrato vence en ≤30 días."""
    try:
        db = get_session()
        actualizados = EstudianteService.actualizar_estados_por_vencimiento(db)
        db.close()
        return respuesta_exito(
            {'actualizados': actualizados},
            f"{actualizados} estudiante(s) actualizados a 'Por Finalizar'"
        )
    except Exception as e:
        return respuesta_error(f"Error al revisar estados: {str(e)}", 500)


# Búsquedas especializadas
@bp.route('/documento/<numero_documento>', methods=['GET'])
def obtener_por_documento(numero_documento):
    """Obtiene un estudiante por número de documento"""
    try:
        db = get_session()
        estudiante = EstudianteService.obtener_estudiante_por_documento(db, numero_documento)
        db.close()
        
        if not estudiante:
            return respuesta_error("Estudiante no encontrado", 404)
        
        return respuesta_exito(estudiante.to_dict())
    
    except Exception as e:
        return respuesta_error(f"Error: {str(e)}", 500)

@bp.route('/email/<email>', methods=['GET'])
def obtener_por_email(email):
    """Obtiene un estudiante por email"""
    try:
        db = get_session()
        estudiante = EstudianteService.obtener_estudiante_por_email(db, email)
        db.close()
        
        if not estudiante:
            return respuesta_error("Estudiante no encontrado", 404)
        
        return respuesta_exito(estudiante.to_dict())
    
    except Exception as e:
        return respuesta_error(f"Error: {str(e)}", 500)

@bp.route('/disponibles', methods=['GET'])
def listar_disponibles():
    """Lista todos los estudiantes disponibles para prácticas"""
    try:
        db = get_session()
        estudiantes = EstudianteService.obtener_estudiantes_disponibles(db)
        db.close()
        
        datos = [e.to_dict() for e in estudiantes]
        return respuesta_exito(datos, f"Se encontraron {len(datos)} estudiantes disponibles")
    
    except Exception as e:
        return respuesta_error(f"Error: {str(e)}", 500)

@bp.route('/estadisticas/facultad/<int:facultad_id>', methods=['GET'])
def estadisticas_facultad(facultad_id):
    """Obtiene estadísticas de estudiantes por estado en una facultad"""
    try:
        db = get_session()
        estadisticas = EstudianteService.obtener_estadisticas_facultad(db, facultad_id)
        db.close()
        
        return respuesta_exito(estadisticas, "Estadísticas obtenidas")
    
    except Exception as e:
        return respuesta_error(f"Error: {str(e)}", 500)

@bp.route('/estadisticas/carrera/<int:carrera_id>', methods=['GET'])
def estadisticas_carrera(carrera_id):
    """Obtiene estadísticas de estudiantes por estado en una carrera"""
    try:
        db = get_session()
        estadisticas = EstudianteService.obtener_estadisticas_carrera(db, carrera_id)
        db.close()

        return respuesta_exito(estadisticas, "Estadísticas obtenidas")

    except Exception as e:
        return respuesta_error(f"Error: {str(e)}", 500)


# ── CV Endpoints ──────────────────────────────────────────────────────────────

@bp.route('/<int:estudiante_id>/cv', methods=['POST'])
def subir_cv(estudiante_id):
    """
    Sube el CV en PDF de un estudiante.
    Form-data: campo 'cv' con el archivo PDF (máx. 5 MB).
    """
    try:
        if 'cv' not in request.files:
            return respuesta_error("Campo 'cv' requerido en form-data")

        archivo = request.files['cv']
        if not archivo.filename:
            return respuesta_error("No se seleccionó ningún archivo")

        db = get_session()
        estudiante = EstudianteService.obtener_estudiante(db, estudiante_id)
        if not estudiante:
            db.close()
            return respuesta_error("Estudiante no encontrado", 404)

        file_bytes = archivo.read()

        # Eliminar CV anterior si existe
        if estudiante.cv_s3_key:
            CVService.delete_cv(estudiante.cv_s3_key)

        s3_key = CVService.upload_cv(estudiante_id, file_bytes, archivo.filename)

        estudiante.cv_s3_key = s3_key
        estudiante.cv_filename = archivo.filename
        estudiante.cv_upload_date = datetime.utcnow()
        db.commit()
        db.refresh(estudiante)
        db.close()

        return respuesta_exito(estudiante.to_dict(), "CV subido exitosamente", 201)

    except ValueError as e:
        return respuesta_error(str(e), 400)
    except Exception as e:
        return respuesta_error(f"Error al subir CV: {str(e)}", 500)


@bp.route('/<int:estudiante_id>/cv', methods=['GET'])
def ver_cv(estudiante_id):
    """Sirve el PDF del CV directamente desde EFS."""
    try:
        db = get_session()
        estudiante = EstudianteService.obtener_estudiante(db, estudiante_id)
        db.close()

        if not estudiante:
            return respuesta_error("Estudiante no encontrado", 404)
        if not estudiante.cv_s3_key:
            return respuesta_error("El estudiante no tiene CV registrado", 404)

        abs_path = CVService.get_file_path(estudiante.cv_s3_key)
        return send_file(abs_path, mimetype='application/pdf',
                         download_name=estudiante.cv_filename or 'cv.pdf',
                         as_attachment=False)

    except FileNotFoundError as e:
        return respuesta_error(str(e), 404)
    except Exception as e:
        return respuesta_error(f"Error al obtener CV: {str(e)}", 500)


@bp.route('/<int:estudiante_id>/cv', methods=['DELETE'])
def eliminar_cv(estudiante_id):
    """Elimina el CV de un estudiante."""
    try:
        db = get_session()
        estudiante = EstudianteService.obtener_estudiante(db, estudiante_id)

        if not estudiante:
            db.close()
            return respuesta_error("Estudiante no encontrado", 404)
        if not estudiante.cv_s3_key:
            db.close()
            return respuesta_error("El estudiante no tiene CV registrado", 404)

        CVService.delete_cv(estudiante.cv_s3_key)

        estudiante.cv_s3_key = None
        estudiante.cv_filename = None
        estudiante.cv_upload_date = None
        db.commit()
        db.close()

        return respuesta_exito(None, "CV eliminado exitosamente")

    except Exception as e:
        return respuesta_error(f"Error al eliminar CV: {str(e)}", 500)
