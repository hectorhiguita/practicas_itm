# 🎯 Flujos y Diagramas - Practicas ITM

## 1. Flujo de Creación de Estudiante

```
┌─────────────────────────────────────────────────────────────┐
│ FLUJO DE CREACIÓN DE ESTUDIANTE                             │
└─────────────────────────────────────────────────────────────┘

1. Admin/Sistema
   ├─ POST /api/facultades/
   │  └─→ Crear Facultad (Ingeniería)
   │
   ├─ POST /api/carreras/
   │  └─→ Crear Carrera (Ing. Sistemas, facultad_id=1)
   │
   └─ POST /api/estudiantes/
      ├─ Validar documento (único)
      ├─ Validar email (único)
      ├─ Validar facultad existe
      ├─ Validar carrera existe
      ├─ Crear registro
      └─→ Estado = "Disponible" 🟢

2. Base de Datos
   ├─ facultades (1 registro)
   ├─ carreras (1 registro)
   └─ estudiantes (1 registro con estado DISPONIBLE)

3. Cliente
   └─→ Puede hacer búsquedas y filtrados
```

---

## 2. Estados de Práctica (Máquina de Estados)

```
                    ┌──────────────┐
                    │   DISPONIBLE │
                    │      🟢      │
                    └──────────────┘
                           │
                   ┌─ Empresa selecciona
                   │
                   ▼
                    ┌──────────────┐
                    │  CONTRATADO  │
                    │      🟡      │
                    └──────────────┘
                           │
                   ┌─ Práctica en curso
                   │
                   ▼
                    ┌──────────────┐
                    │ POR FINALIZAR│
                    │      🔴      │
                    └──────────────┘
                           │
                   ┌─ Finalización
                   │
                   ▼
                    ┌──────────────┐
                    │   FINALIZÓ   │
                    │      ⚫      │
                    └──────────────┘
                           │
                      (No reversible)
                           │
                           ▼
                    [ARCHIVADO]
```

---

## 3. Arquitectura de Capas

```
┌─────────────────────────────────────────────────────────────┐
│ CAPA 1: CLIENTE HTTP                                        │
│  ┌─────────┐ ┌─────────┐ ┌──────────┐                      │
│  │ Browser │ │  cURL   │ │ API Test │                      │
│  └────┬────┘ └────┬────┘ └────┬─────┘                      │
└───────┼────────────┼─────────────┼──────────────────────────┘
        │            │             │
        ▼            ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│ CAPA 2: API REST (Flask)                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ health_check()                                      │   │
│  │ GET / POST / PUT / DELETE                           │   │
│  │ - /api/estudiantes/...  (7 endpoints)               │   │
│  │ - /api/facultades/...   (5 endpoints)               │   │
│  │ - /api/carreras/...     (5 endpoints)               │   │
│  └──────────────────────┬──────────────────────────────┘   │
└────────────────────────┼──────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ CAPA 3: SERVICIOS (Lógica de Negocio)                       │
│  ┌──────────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ EstudianteService│  │FacultadServ. │  │CarreraServ.  │  │
│  │ - 13 métodos     │  │ - 6 métodos  │  │ - 6 métodos  │  │
│  │ - Validaciones   │  │ - CRUD       │  │ - CRUD       │  │
│  │ - Búsquedas      │  │              │  │              │  │
│  │ - Estadísticas   │  │              │  │              │  │
│  └────────┬─────────┘  └────────┬─────┘  └────────┬─────┘  │
└───────────┼─────────────────────┼──────────────────┼────────┘
            │                     │                  │
            ▼                     ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│ CAPA 4: MODELOS (SQLAlchemy ORM)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Facultad    │  │   Carrera    │  │  Estudiante  │      │
│  │ - id         │  │ - id         │  │ - id         │      │
│  │ - nombre     │  │ - nombre     │  │ - documento  │      │
│  │ - relacionEn │  │ - facultad_id│  │ - nombre     │      │
│  │   (1:N)      │  │ - relacionEn │  │ - estado     │      │
│  │              │  │   (1:N)      │  │ - facultad   │      │
│  │              │  │              │  │ - carrera    │      │
│  └────────┬─────┘  └────────┬─────┘  └────────┬─────┘      │
└───────────┼─────────────────┼──────────────────┼────────────┘
            │                 │                  │
            ▼                 ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│ CAPA 5: BASE DE DATOS (PostgreSQL)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  facultades  │  │   carreras   │  │  estudiantes │      │
│  │ (id, nombre) │  │ (id, nombre, │  │ (id, doc,    │      │
│  │              │  │  facultad_id)│  │  nombre,     │      │
│  │              │  │              │  │  estado...)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Relaciones de Base de Datos

```
┌──────────────────┐
│   FACULTADES     │
├──────────────────┤
│ id (PK)          │
│ nombre           │◄──┐
│ descripcion      │   │
│ fecha_creacion   │   │ 1:N
└──────────────────┘   │
       ▲                │
       │                │
       │ 1:N            │
       │                │
┌──────────────────┐   │    ┌──────────────────┐
│    CARRERAS      │───┘    │   ESTUDIANTES    │
├──────────────────┤        ├──────────────────┤
│ id (PK)          │        │ id (PK)          │
│ nombre           │        │ numero_documento │
│ facultad_id (FK) │        │ nombre           │
│ descripcion      │        │ apellido         │
│ fecha_creacion   │◄───────│ email            │
└──────────────────┘ 1:N    │ genero           │
                            │ estado_practica  │
                            │ facultad_id (FK) │
                            │ carrera_id (FK)  │
                            │ fecha_creacion   │
                            │ fecha_actualiz.  │
                            └──────────────────┘
```

---

## 5. Flujo de API: Crear Estudiante

```
CLIENT                          API                    SERVICES              DATABASE
   │                            │                         │                    │
   │ POST /api/estudiantes/     │                         │                    │
   │ {datos}                    │                         │                    │
   ├────────────────────────────>                         │                    │
   │                            │ Validar JSON            │                    │
   │                            │ ├─ Campos obligatorios  │                    │
   │                            │ ├─ Tipos de datos       │                    │
   │                            │ └─ Estructura           │                    │
   │                            │                         │                    │
   │                            │ EstudianteService.      │                    │
   │                            │ crear_estudiante()      │                    │
   │                            ├────────────────────────>│                    │
   │                            │                         │ SELECT documento   │
   │                            │                         ├───────────────────>│
   │                            │                         │<─ No existe        │
   │                            │                         │ SELECT email       │
   │                            │                         ├───────────────────>│
   │                            │                         │<─ No existe        │
   │                            │                         │ INSERT estudiante  │
   │                            │                         ├───────────────────>│
   │                            │                         │<─ Creado (id=1)    │
   │                            │<─ objeto estudiante ────┤                    │
   │                            │                         │                    │
   │<── 201 Created ─────────────┤                         │                    │
   │ {estudiante}               │                         │                    │
   │                            │                         │                    │
```

---

## 6. Flujo de API: Listar con Filtros

```
CLIENT                          API                    SERVICES              DATABASE
   │                            │                         │                    │
   │ GET /api/estudiantes/      │                         │                    │
   │ ?facultad_id=1             │                         │                    │
   │ &estado=disponible         │                         │                    │
   ├────────────────────────────>                         │                    │
   │                            │ Parsear parámetros      │                    │
   │                            │ ├─ facultad_id=1        │                    │
   │                            │ └─ estado=disponible    │                    │
   │                            │                         │                    │
   │                            │ EstudianteService.      │                    │
   │                            │ obtener_estudiantes..() │                    │
   │                            ├────────────────────────>│                    │
   │                            │                         │ SELECT * FROM      │
   │                            │                         │ estudiantes WHERE   │
   │                            │                         │ facultad_id=1 AND   │
   │                            │                         │ estado='Disponible' │
   │                            │                         ├───────────────────>│
   │                            │                         │<─ [est1, est2, ..]│
   │                            │<─ lista estudiantes ────┤                    │
   │                            │                         │                    │
   │<── 200 OK ──────────────────┤                         │                    │
   │ {datos: [est1, est2]}      │                         │                    │
   │                            │                         │                    │
```

---

## 7. Flujo de Testing

```
┌────────────────────────────────────────────────┐
│ SUITE DE TESTS                                 │
├────────────────────────────────────────────────┤
│                                                │
├─ test_database.py                             │
│  ├─ test_conexion_base_datos()                │
│  ├─ test_crear_tablas()                       │
│  └─ test_crear_facultad()                     │
│                                                │
├─ test_estudiantes.py                          │
│  ├─ test_crear_estudiante()                   │
│  ├─ test_obtener_estudiante()                 │
│  ├─ test_actualizar_estado_practica()         │
│  ├─ test_obtener_estudiantes_disponibles()    │
│  └─ test_eliminar_estudiante()                │
│                                                │
└─ test_api.py                                  │
   ├─ test_health_check()                       │
   ├─ test_index()                              │
   ├─ test_crear_facultad()                     │
   ├─ test_listar_facultades()                  │
   └─ test_endpoint_no_encontrado()             │
                                                │
└─→ pytest -v  (8+ tests con fixtures)
    └─→ ✅ Todos pasan
```

---

## 8. Ciclo de Vida de Datos

```
EVENTO                  ACCIÓN              ESTADO BD         NOTIFICACIÓN
  │                       │                     │                   │
  ├─ Crear Facultad       │                     │                   │
  │  "Ingeniería"         └─→ INSERT            │ 1 facultad        │
  │                           facultades       │                   │
  │                                            │                   │
  ├─ Crear Carrera        │                    │                   │
  │  "Ing. Sistemas"       └─→ INSERT           │ 1 carrera         │
  │  facultad_id=1             carreras        │ asoc. a facultad  │
  │                                            │                   │
  ├─ Registrar Estudiante  │                    │                   │
  │  doc="123"             └─→ INSERT           │ 1 estudiante      │
  │  estado="Disponible"        estudiantes    │ DISPONIBLE        │
  │  facultad=1                                │                   │
  │  carrera=1                                 │                   │
  │                                            │                   │
  ├─ Cambiar Estado       │                    │                   │
  │  a "Contratado"        └─→ UPDATE          │ Estudiante        │
  │                            estudiantes    │ CONTRATADO        │
  │                            SET estado=... │                   │
  │                                            │                   │
  ├─ Finalizar           │                    │                   │
  │  Estado "Finalizó"     └─→ UPDATE          │ Estudiante        │
  │                            estudiantes    │ FINALIZÓ          │
  │                                            │                   │
  └─ Archivar            │                    │                   │
     (Futuro: soft delete) └─→ UPDATE          │ is_active=False   │
                              UPDATE           │ (Versión 2.0)     │
```

---

## 9. Estructura de Respuesta JSON

```
ÉXITO (200, 201):
{
  "mensaje": "Descripción",
  "datos": {
    "id": 1,
    "campo1": "valor1",
    "campo2": "valor2",
    ...
  }
}

LISTA (200):
{
  "mensaje": "Se encontraron 5 registros",
  "datos": [
    { "id": 1, ... },
    { "id": 2, ... },
    ...
  ]
}

ERROR (400, 404, 500):
{
  "error": "Descripción del error"
}

ESTADÍSTICAS (200):
{
  "mensaje": "Estadísticas obtenidas",
  "datos": {
    "total": 10,
    "disponible": 5,
    "contratado": 3,
    "por_finalizar": 1,
    "finalizo": 1
  }
}
```

---

## 10. Decisiones de Diseño

### Decisión 1: Separar en 3 Capas
```
API (REST) → Services (Lógica) → ORM (Datos)
```
**Por qué:** Facilita testing, mantenimiento y escalabilidad

### Decisión 2: Usar Enum para Estados
```
EstadoPractica.DISPONIBLE
EstadoPractica.CONTRATADO
EstadoPractica.POR_FINALIZAR
EstadoPractica.FINALIZO
```
**Por qué:** Type safety y evita errores de tipeo

### Decisión 3: Validaciones en Services
```
EstudianteService.crear_estudiante()
├─ Verificar documento único
├─ Verificar email único
├─ Validar género
└─ Validar existencia de facultad/carrera
```
**Por qué:** Lógica centralizada y reutilizable

### Decisión 4: Relaciones 1:N
```
Facultad 1 ──→ N Carreras
Facultad 1 ──→ N Estudiantes
Carrera 1 ──→ N Estudiantes
```
**Por qué:** Integridad referencial y queries eficientes

---

**Última actualización:** Marzo 12, 2026  
**Versión del proyecto:** 1.0.0
