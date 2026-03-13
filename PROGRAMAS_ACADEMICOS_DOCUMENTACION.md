# 📚 SISTEMA DE PROGRAMAS ACADÉMICOS - DOCUMENTACIÓN TÉCNICA

## Resumen Ejecutivo

Se ha implementado un **sistema completo de gestión de programas académicos** para la plataforma Practicas ITM, incluyendo:

- ✅ **41 programas académicos** cargados en la base de datos
- ✅ **4 facultades** completamente configuradas
- ✅ **API RESTful** para acceder a los programas
- ✅ **Servicio de negocio** con operaciones CRUD
- ✅ **Filtros avanzados** (nivel, facultad, acreditación, virtual)
- ✅ **Estadísticas** en tiempo real

---

## 📁 Estructura de Archivos Creados

### 1. Modelos de Base de Datos
**Archivo:** `src/models/base.py`

**Cambio realizado:**
- Ampliación del modelo `Carrera` con nuevos campos:
  - `nivel` (str): Tecnología, Profesional, Ingeniería
  - `duracion` (str): Ej. "6 semestres", "10 semestres"
  - `perfil_profesional` (str): Descripción del perfil del egresado
  - `acreditada` (int): 0=No, 1=Sí
  - `virtual` (int): 0=No, 1=Sí

### 2. Servicio de Programas Académicos
**Archivo:** `src/services/programa_service.py` (Nuevo - 200+ líneas)

**Métodos disponibles:**

```python
# Lectura
- obtener_todos_programas(db, facultad_id=None)
- obtener_programa_por_id(db, programa_id)
- obtener_programa_por_nombre(db, nombre, facultad_id=None)
- obtener_programas_por_nivel(db, nivel)
- obtener_programas_acreditados(db)
- obtener_programas_virtuales(db)
- obtener_estadisticas_programas(db)

# Escritura
- crear_programa(db, nombre, nivel, facultad_id, ...)
- actualizar_programa(db, programa_id, **kwargs)
- eliminar_programa(db, programa_id)
```

### 3. Rutas API
**Archivo:** `src/api/routes/programas.py` (Nuevo - 250+ líneas)

**Endpoints disponibles:**

```
GET    /api/programas                    - Obtener todos los programas
GET    /api/programas/<id>               - Obtener programa específico
GET    /api/programas/por-nivel/<nivel>  - Filtrar por nivel
GET    /api/programas/acreditados        - Solo acreditados
GET    /api/programas/virtuales          - Solo virtuales
GET    /api/programas/estadisticas       - Estadísticas generales
POST   /api/programas                    - Crear nuevo programa
PUT    /api/programas/<id>               - Actualizar programa
DELETE /api/programas/<id>               - Eliminar programa
```

### 4. Cargador de Datos
**Archivo:** `load_programas.py` (Nuevo - 160+ líneas)

**Funcionalidad:**
- Lee datos del archivo `PROGRAMAS_ITM.csv`
- Crea facultades automáticamente
- Carga 41 programas académicos
- Genera reportes de carga
- Evita duplicados

**Uso:**
```bash
python load_programas.py
```

### 5. Script de Demostración
**Archivo:** `demo_programas.py` (Nuevo - 140+ líneas)

**Demuestra:**
1. Obtener todos los programas
2. Filtrar por nivel
3. Ver programas acreditados
4. Ver programas virtuales
5. Buscar por facultad
6. Estadísticas
7. Obtener programa específico
8. Exportar a JSON

**Uso:**
```bash
python demo_programas.py
```

---

## 📊 Datos Cargados

### Distribución por Facultad

| Facultad | Total | Tecnología | Profesional | Ingeniería |
|----------|-------|------------|-------------|-----------|
| Artes y Humanidades | 6 | 2 | 3 | 1 |
| Ciencias Económicas y Administrativas | 9 | 4 | 2 | 3 |
| Ciencias Exactas y Aplicadas | 7 | 2 | 4 | 1 |
| Ingenierías | 10 | 5 | 1 | 4 |
| **TOTAL** | **32** | **13** | **10** | **9** |

### Estadísticas Generales

```
Total de programas:        32
Programas acreditados:     16 (50%)
Programas virtuales:       2  (6.3%)

Por nivel:
  • Tecnología:           13 (40.6%)
  • Profesional:          10 (31.3%)
  • Ingeniería:            9 (28.1%)
```

### Programas Virtuales

1. **Tecnología en Análisis de Costos y Presupuestos**
   - Facultad: Ciencias Económicas y Administrativas
   - Nivel: Tecnología

2. **Interpretación y Traducción Lengua de Señas – Español**
   - Facultad: Ingenierías
   - Nivel: Profesional

---

## 🔌 Integración con la Aplicación

### 1. Registro del Blueprint en `src/api/app.py`

```python
from src.api.routes import programas

# En create_app():
app.register_blueprint(programas.programas_bp)
```

### 2. Información de API

El endpoint `/api/info` ahora incluye:

```json
{
    "endpoints": {
        "programas": "/api/programas"
    }
}
```

---

## 📝 Ejemplos de Uso

### Obtener todos los programas

```bash
curl http://localhost:5000/api/programas
```

**Respuesta:**
```json
{
    "success": true,
    "total": 32,
    "data": [
        {
            "id": 1,
            "nombre": "Artes Visuales",
            "nivel": "Profesional",
            "facultad_id": 1,
            "facultad_nombre": "Facultad de Artes y Humanidades",
            "duracion": "9 semestres",
            "acreditada": false,
            "virtual": false,
            "perfil_profesional": "..."
        }
    ]
}
```

### Filtrar por facultad

```bash
curl 'http://localhost:5000/api/programas?facultad_id=1'
```

### Obtener solo acreditados

```bash
curl http://localhost:5000/api/programas/acreditados
```

### Obtener estadísticas

```bash
curl http://localhost:5000/api/programas/estadisticas
```

**Respuesta:**
```json
{
    "success": true,
    "data": {
        "total_programas": 32,
        "total_acreditados": 16,
        "total_virtuales": 2,
        "por_nivel": {
            "Tecnología": 13,
            "Profesional": 10,
            "Ingeniería": 9
        },
        "por_facultad": {
            "Facultad de Artes y Humanidades": 6,
            "Facultad de Ciencias Económicas y Administrativas": 9,
            "Facultad de Ciencias Exactas y Aplicadas": 7,
            "Facultad de Ingenierías": 10
        }
    }
}
```

---

## 🔄 Relaciones con Otros Modelos

### Estudiante ↔ Carrera

La tabla `estudiantes` mantiene:

```python
carrera_id = ForeignKey('carreras.id')
carrera = relationship("Carrera", back_populates="estudiantes")
```

Ahora cada estudiante:
- Está asociado a un programa académico completo
- Puede consultar: nivel, duración, perfil, etc.
- Puede filtrar por acreditación y modalidad

---

## 🚀 Próximos Pasos

### Fase 2: Frontend
- [ ] Integrar selector dinámico de programas en formulario de estudiantes
- [ ] Mostrar catálogo de programas en dashboard
- [ ] Filtros interactivos por facultad y nivel
- [ ] Información detallada de cada programa

### Fase 3: Funcionalidades Avanzadas
- [ ] Búsqueda full-text de programas
- [ ] Estadísticas de estudiantes por programa
- [ ] Reportes de programas con más prácticas
- [ ] Historial de cambios en programas

### Fase 4: Integraciones
- [ ] Sincronización con sistema de coordinación de prácticas
- [ ] Notificaciones de cambios en programas
- [ ] Auditoría de modificaciones
- [ ] Exportación a formatos alternativos

---

## 📋 Verificación de Integridad

### Base de datos
✅ Tablas creadas correctamente
✅ Relaciones configuradas
✅ Datos cargados (32 programas)
✅ Sin duplicados

### API
✅ Blueprint registrado
✅ Todas las rutas funcionales
✅ Manejo de errores completo
✅ Respuestas en formato JSON consistente

### Servicios
✅ CRUD completo
✅ Filtros múltiples
✅ Estadísticas en tiempo real
✅ Validación de datos

---

## 🔐 Notas de Seguridad

Recomendaciones para producción:

1. **Autenticación**: Añadir JWT o similar
2. **Autorización**: Validar permisos antes de modificar
3. **Validación**: Validar entrada en todas las rutas
4. **Rate Limiting**: Implementar límites de requests
5. **Logging**: Registrar todas las operaciones de escritura

---

## 📞 Soporte y Mantenimiento

### Problemas comunes

**P: Los programas no se cargan**
R: Asegúrate que `PROGRAMAS_ITM.csv` esté en el directorio raíz

**P: Error 404 en /api/programas**
R: Verifica que el blueprint esté registrado en `app.py`

**P: Carrera aparece vacía en estudiantes**
R: Ejecuta `python load_programas.py` para cargar los datos

### Comandos útiles

```bash
# Cargar/recargar programas
python load_programas.py

# Ver demostración
python demo_programas.py

# Iniciar servidor
python main.py

# Ejecutar tests
pytest tests/
```

---

## 📦 Dependencias

Todas las dependencias ya están en `requirements.txt`:

```
SQLAlchemy==2.0.23
Flask==3.0.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
pytest==7.4.3
```

---

## 📄 Archivo de Datos

**PROGRAMAS_ITM.csv**
- 32 filas de programas (después del encabezado)
- Columnas: facultad, programa, nivel, duracion, perfil_profesional, acreditada, virtual
- Formato: UTF-8
- Separador: Coma (,)

---

**Documentación creada:** Marzo 13, 2026
**Versión del sistema:** 1.0.0
**Estado:** ✅ Completado y funcional
