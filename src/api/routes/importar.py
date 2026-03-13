"""
Endpoint para importar estudiantes desde CSV o Excel.
Normaliza datos automáticamente y reporta errores por fila y campo.
"""
import csv
import io
import difflib
from flask import Blueprint, request, jsonify, Response
from src.database.connection import get_session
from src.models.base import Carrera
from src.services.estudiante_service import EstudianteService

importar_bp = Blueprint('importar', __name__, url_prefix='/api/importar')

# ── Mapeos de normalización ──────────────────────────────────────────────────

GENERO_MAP = {
    'masculino': 'Masculino', 'm': 'Masculino', 'hombre': 'Masculino',
    'masc': 'Masculino', 'h': 'Masculino', 'male': 'Masculino',
    'femenino': 'Femenino', 'f': 'Femenino', 'mujer': 'Femenino',
    'fem': 'Femenino', 'female': 'Femenino',
    'no binario': 'No Binario', 'nobinario': 'No Binario', 'nb': 'No Binario',
    'no-binario': 'No Binario', 'non binary': 'No Binario',
    'hombre transgénero': 'Hombre Transgénero', 'hombre transgenero': 'Hombre Transgénero',
    'trans m': 'Hombre Transgénero', 'trans masculino': 'Hombre Transgénero',
    'mujer transgénero': 'Mujer Transgénero', 'mujer transgenero': 'Mujer Transgénero',
    'trans f': 'Mujer Transgénero', 'trans femenino': 'Mujer Transgénero',
    'genderqueer': 'Genderqueer',
    'asexual': 'Asexual',
    'otro': 'Otro', 'other': 'Otro',
    'prefiero no decir': 'Prefiero no decir', 'no especifica': 'Prefiero no decir',
    'no especifico': 'Prefiero no decir', 'sin especificar': 'Prefiero no decir',
    'prefiero no especificar': 'Prefiero no decir',
}

ESTADO_MAP = {
    'disponible': 'Disponible',
    'contratado': 'Contratado',
    'por finalizar': 'Por Finalizar', 'porfinalizar': 'Por Finalizar',
    'por_finalizar': 'Por Finalizar', 'en practica': 'Por Finalizar',
    'finalizo': 'Finalizó', 'finalizó': 'Finalizó',
    'finalizado': 'Finalizó', 'terminado': 'Finalizó',
}

# Aliases para nombres de columnas
ALIAS_COLUMNAS = {
    'documento': 'numero_documento', 'doc': 'numero_documento',
    'cedula': 'numero_documento', 'cc': 'numero_documento',
    'id_estudiante': 'numero_documento', 'no_documento': 'numero_documento',
    'nombres': 'nombre', 'primer_nombre': 'nombre',
    'apellidos': 'apellido', 'primer_apellido': 'apellido',
    'correo': 'email', 'correo_electronico': 'email', 'mail': 'email',
    'tel': 'telefono', 'cel': 'telefono', 'celular': 'telefono', 'movil': 'telefono',
    'carrera': 'programa', 'programa_academico': 'programa',
    'carrera_programa': 'programa', 'programa_carrera': 'programa',
    'sexo': 'genero', 'genero_sexual': 'genero',
    'estado': 'estado_practica',
    'discapacidad': 'tiene_discapacidad',
}

COLUMNAS_REQUERIDAS = {'numero_documento', 'nombre', 'apellido', 'email', 'telefono', 'genero', 'programa'}

PLANTILLA_CSV = (
    'numero_documento,nombre,apellido,email,telefono,genero,programa,estado_practica,tiene_discapacidad\n'
    '1001234567,Juan Carlos,Garcia Lopez,juan.garcia@itm.edu.co,3001234567,Masculino,Ingeniería de Sistemas,Disponible,\n'
    '1002345678,Maria Alejandra,Lopez Restrepo,maria.lopez@itm.edu.co,3012345678,Femenino,Tecnología en Sistemas de Información,Disponible,\n'
    '1003456789,Ana Sofia,Ramirez Gomez,ana.ramirez@itm.edu.co,3023456789,Femenino,Ingeniería Biomédica,Contratado,\n'
)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _normalizar_nombre(valor: str) -> str:
    """Title-case con colapso de espacios múltiples."""
    return ' '.join(w.capitalize() for w in valor.strip().split()) if valor else ''


def _normalizar_genero(valor: str):
    return GENERO_MAP.get((valor or '').lower().strip())


def _normalizar_estado(valor: str) -> str:
    return ESTADO_MAP.get((valor or '').lower().strip(), 'Disponible')


def _buscar_programa(nombre_buscar: str, programas: list):
    """
    Busca el programa más cercano usando tres estrategias en orden:
    1. Coincidencia exacta (case-insensitive)
    2. Coincidencia por contenido (substring bidireccional)
    3. Coincidencia difusa (difflib, umbral 0.45)

    Devuelve (Carrera | None, sugerencias: list[str])
    """
    if not nombre_buscar or not nombre_buscar.strip():
        return None, []

    buscar = nombre_buscar.strip().lower()
    nombres = [p.nombre for p in programas]

    # 1. Exacta
    for p in programas:
        if p.nombre.lower() == buscar:
            return p, []

    # 2. Substring bidireccional
    candidatos = [p for p in programas
                  if buscar in p.nombre.lower() or p.nombre.lower() in buscar]
    if candidatos:
        mejor = max(candidatos, key=lambda p: len(p.nombre))
        otros = [p.nombre for p in candidatos if p is not mejor][:2]
        return mejor, otros

    # 3. Difusa
    matches = difflib.get_close_matches(nombre_buscar, nombres, n=3, cutoff=0.45)
    if matches:
        mejor = next(p for p in programas if p.nombre == matches[0])
        return mejor, matches[1:]

    return None, []


def _normalizar_columnas(fila: dict) -> dict:
    resultado = {}
    for key, val in fila.items():
        key_norm = (key or '').lower().strip().replace(' ', '_').replace('-', '_')
        key_std = ALIAS_COLUMNAS.get(key_norm, key_norm)
        resultado[key_std] = (val or '').strip()
    return resultado


def _leer_csv(contenido: bytes) -> list:
    texto = contenido.decode('utf-8-sig')  # utf-8-sig maneja BOM de Excel
    return list(csv.DictReader(io.StringIO(texto)))


def _leer_excel(contenido: bytes) -> list:
    try:
        import openpyxl
    except ImportError:
        raise ImportError('openpyxl requerido para Excel. Instale con: pip install openpyxl')

    wb = openpyxl.load_workbook(io.BytesIO(contenido), read_only=True, data_only=True)
    ws = wb.active
    filas = list(ws.iter_rows(values_only=True))
    if not filas:
        return []

    encabezados = [str(h).strip() if h is not None else f'col_{i}' for i, h in enumerate(filas[0])]
    resultado = []
    for fila in filas[1:]:
        if all(c is None for c in fila):
            continue
        resultado.append({
            encabezados[i]: (str(fila[i]).strip() if fila[i] is not None else '')
            for i in range(len(encabezados))
        })
    return resultado


# ── Endpoints ────────────────────────────────────────────────────────────────

@importar_bp.route('/estudiantes', methods=['POST'])
def importar_estudiantes():
    """
    Importa estudiantes desde un archivo CSV o Excel.
    Campo multipart: 'archivo'
    """
    if 'archivo' not in request.files:
        return jsonify({'error': 'Se requiere el campo "archivo" en el form-data'}), 400

    archivo = request.files['archivo']
    if not archivo.filename:
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400

    nombre_archivo = archivo.filename.lower()
    contenido = archivo.read()

    try:
        if nombre_archivo.endswith('.csv'):
            filas_raw = _leer_csv(contenido)
        elif nombre_archivo.endswith(('.xlsx', '.xls')):
            filas_raw = _leer_excel(contenido)
        else:
            return jsonify({'error': 'Formato no soportado. Use .csv o .xlsx'}), 400
    except ImportError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': f'Error al leer el archivo: {str(e)}'}), 400

    if not filas_raw:
        return jsonify({'error': 'El archivo está vacío o sin datos'}), 400

    filas = [_normalizar_columnas(f) for f in filas_raw]

    # Verificar columnas requeridas en la primera fila
    cols_presentes = set(filas[0].keys())
    cols_faltantes = COLUMNAS_REQUERIDAS - cols_presentes
    if cols_faltantes:
        return jsonify({
            'error': f'Columnas requeridas faltantes: {", ".join(sorted(cols_faltantes))}',
            'columnas_encontradas': sorted(cols_presentes),
            'columnas_requeridas': sorted(COLUMNAS_REQUERIDAS),
            'ayuda': 'Descargue la plantilla en /api/importar/estudiantes/plantilla',
        }), 400

    db = get_session()
    try:
        programas = db.query(Carrera).all()
        importados = []
        errores = []

        for num_fila, fila in enumerate(filas, start=2):  # fila 1 = encabezados
            fila_errores = []
            datos = {}

            # numero_documento
            doc = fila.get('numero_documento', '').strip()
            if not doc:
                fila_errores.append({'campo': 'numero_documento', 'valor': doc,
                                     'mensaje': 'El número de documento es obligatorio'})
            else:
                datos['numero_documento'] = doc

            # nombre
            nombre_val = _normalizar_nombre(fila.get('nombre', ''))
            if not nombre_val:
                fila_errores.append({'campo': 'nombre', 'valor': fila.get('nombre', ''),
                                     'mensaje': 'El nombre es obligatorio'})
            else:
                datos['nombre'] = nombre_val

            # apellido
            apellido_val = _normalizar_nombre(fila.get('apellido', ''))
            if not apellido_val:
                fila_errores.append({'campo': 'apellido', 'valor': fila.get('apellido', ''),
                                     'mensaje': 'El apellido es obligatorio'})
            else:
                datos['apellido'] = apellido_val

            # email
            email_val = fila.get('email', '').lower().strip()
            dominio = email_val.split('@')[-1] if '@' in email_val else ''
            if not email_val or '@' not in email_val or '.' not in dominio:
                fila_errores.append({'campo': 'email', 'valor': fila.get('email', ''),
                                     'mensaje': 'Email inválido o vacío'})
            else:
                datos['email'] = email_val

            # telefono (solo dígitos y +)
            tel_raw = fila.get('telefono', '')
            datos['telefono'] = ''.join(c for c in tel_raw if c.isdigit() or c == '+') or tel_raw.strip()

            # genero
            genero_raw = fila.get('genero', '')
            genero_val = _normalizar_genero(genero_raw)
            if not genero_val:
                opciones = ', '.join(sorted(set(GENERO_MAP.values())))
                fila_errores.append({'campo': 'genero', 'valor': genero_raw,
                                     'mensaje': f'Género no reconocido. Opciones válidas: {opciones}'})
            else:
                datos['genero'] = genero_val

            # programa → carrera_id + facultad_id (con fuzzy matching)
            programa_raw = fila.get('programa', '').strip()
            programa, sugerencias = _buscar_programa(programa_raw, programas)
            if not programa:
                msg = f'No se encontró el programa "{programa_raw}"'
                if sugerencias:
                    msg += f'. ¿Quiso decir: "{sugerencias[0]}"?'
                fila_errores.append({'campo': 'programa', 'valor': programa_raw, 'mensaje': msg})
            else:
                datos['carrera_id'] = programa.id
                datos['facultad_id'] = programa.facultad_id
                if programa.nombre.lower() != programa_raw.lower():
                    datos['_programa_normalizado'] = programa.nombre

            # estado_practica (opcional, default Disponible)
            datos['estado_practica'] = _normalizar_estado(fila.get('estado_practica', ''))

            # discapacidad (opcional)
            datos['tiene_discapacidad'] = fila.get('tiene_discapacidad', '').strip() or None
            datos['discapacidad_personalizada'] = fila.get('discapacidad_personalizada', '').strip() or None

            if fila_errores:
                errores.append({'fila': num_fila, 'errores': fila_errores})
                continue

            # Intentar crear el estudiante
            try:
                est = EstudianteService.crear_estudiante(
                    db,
                    numero_documento=datos['numero_documento'],
                    nombre=datos['nombre'],
                    apellido=datos['apellido'],
                    email=datos['email'],
                    telefono=datos.get('telefono'),
                    genero=datos['genero'],
                    carrera_id=datos['carrera_id'],
                    facultad_id=datos['facultad_id'],
                )

                if datos['estado_practica'] != 'Disponible':
                    EstudianteService.actualizar_estado_practica(db, est.id, datos['estado_practica'])

                if datos.get('tiene_discapacidad'):
                    EstudianteService.actualizar_estudiante(
                        db, est.id,
                        tiene_discapacidad=datos['tiene_discapacidad'],
                        discapacidad_personalizada=datos.get('discapacidad_personalizada'),
                    )

                resultado = est.to_dict()
                if '_programa_normalizado' in datos:
                    resultado['_programa_normalizado'] = datos['_programa_normalizado']
                importados.append(resultado)

            except ValueError as e:
                errores.append({'fila': num_fila,
                                'errores': [{'campo': 'datos', 'valor': '', 'mensaje': str(e)}]})
            except Exception as e:
                errores.append({'fila': num_fila,
                                'errores': [{'campo': 'sistema', 'valor': '',
                                             'mensaje': f'Error inesperado: {str(e)}'}]})

        return jsonify({
            'total_filas': len(filas),
            'exitosos': len(importados),
            'con_errores': len(errores),
            'importados': importados,
            'errores': errores,
        }), 200

    finally:
        db.close()


@importar_bp.route('/estudiantes/plantilla', methods=['GET'])
def descargar_plantilla():
    """Descarga una plantilla CSV de ejemplo."""
    return Response(
        PLANTILLA_CSV,
        mimetype='text/csv; charset=utf-8',
        headers={'Content-Disposition': 'attachment; filename=plantilla_estudiantes.csv'},
    )
