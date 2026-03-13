# Documentación de la API - Practicas ITM

## Descripción General

API REST para la gestión de prácticas universitarias. Permite administrar estudiantes, facultades y carreras con control de estados de práctica.

## Base URL

```
http://localhost:5000/api
```

## Autenticación

Actualmente no se requiere autenticación. En versiones futuras se implementará JWT.

## Endpoints

### Health Check

#### Verificar estado de la aplicación
```
GET /health
```

**Respuesta exitosa (200):**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

## FACULTADES

### Listar todas las facultades
```
GET /api/facultades/
```

**Respuesta exitosa (200):**
```json
{
  "mensaje": "Se encontraron 2 facultades",
  "datos": [
    {
      "id": 1,
      "nombre": "Ingeniería",
      "descripcion": "Facultad de Ingeniería",
      "fecha_creacion": "2026-03-12T10:30:00"
    }
  ]
}
```

### Obtener una facultad
```
GET /api/facultades/{facultad_id}
```

**Parámetros:**
- `facultad_id` (int): ID de la facultad

**Respuesta exitosa (200):**
```json
{
  "datos": {
    "id": 1,
    "nombre": "Ingeniería",
    "descripcion": "Facultad de Ingeniería",
    "fecha_creacion": "2026-03-12T10:30:00"
  }
}
```

### Crear una facultad
```
POST /api/facultades/
```

**Body JSON requerido:**
```json
{
  "nombre": "Ingeniería",
  "descripcion": "Facultad de Ingeniería"
}
```

**Respuesta exitosa (201):**
```json
{
  "mensaje": "Facultad creada exitosamente",
  "datos": {
    "id": 1,
    "nombre": "Ingeniería",
    "descripcion": "Facultad de Ingeniería",
    "fecha_creacion": "2026-03-12T10:30:00"
  }
}
```

### Actualizar una facultad
```
PUT /api/facultades/{facultad_id}
```

**Body JSON (campos opcionales):**
```json
{
  "nombre": "Ingeniería (Actualizado)",
  "descripcion": "Nueva descripción"
}
```

**Respuesta exitosa (200):**
```json
{
  "mensaje": "Facultad actualizada exitosamente",
  "datos": { ... }
}
```

### Eliminar una facultad
```
DELETE /api/facultades/{facultad_id}
```

**Respuesta exitosa (200):**
```json
{
  "mensaje": "Facultad eliminada exitosamente"
}
```

---

## CARRERAS

### Listar todas las carreras
```
GET /api/carreras/
```

**Parámetros opcionales:**
- `facultad_id` (int): Filtrar por facultad

**Respuesta exitosa (200):**
```json
{
  "mensaje": "Se encontraron 3 carreras",
  "datos": [
    {
      "id": 1,
      "nombre": "Ingeniería de Sistemas",
      "descripcion": "Carrera de Ingeniería de Sistemas",
      "facultad_id": 1,
      "fecha_creacion": "2026-03-12T10:30:00"
    }
  ]
}
```

### Obtener una carrera
```
GET /api/carreras/{carrera_id}
```

**Respuesta exitosa (200):**
```json
{
  "datos": {
    "id": 1,
    "nombre": "Ingeniería de Sistemas",
    "descripcion": "Carrera de Ingeniería de Sistemas",
    "facultad_id": 1,
    "fecha_creacion": "2026-03-12T10:30:00"
  }
}
```

### Crear una carrera
```
POST /api/carreras/
```

**Body JSON requerido:**
```json
{
  "nombre": "Ingeniería de Sistemas",
  "facultad_id": 1,
  "descripcion": "Carrera de Ingeniería de Sistemas"
}
```

**Respuesta exitosa (201):**
```json
{
  "mensaje": "Carrera creada exitosamente",
  "datos": { ... }
}
```

### Actualizar una carrera
```
PUT /api/carreras/{carrera_id}
```

**Body JSON (campos opcionales):**
```json
{
  "nombre": "Ingeniería de Sistemas (Actualizado)",
  "descripcion": "Nueva descripción"
}
```

**Respuesta exitosa (200):**
```json
{
  "mensaje": "Carrera actualizada exitosamente",
  "datos": { ... }
}
```

### Eliminar una carrera
```
DELETE /api/carreras/{carrera_id}
```

**Respuesta exitosa (200):**
```json
{
  "mensaje": "Carrera eliminada exitosamente"
}
```

---

## ESTUDIANTES

### Listar todos los estudiantes
```
GET /api/estudiantes/
```

**Parámetros opcionales:**
- `facultad_id` (int): Filtrar por facultad
- `carrera_id` (int): Filtrar por carrera
- `estado` (str): Filtrar por estado (disponible, contratado, por_finalizar, finalizo)

**Respuesta exitosa (200):**
```json
{
  "mensaje": "Se encontraron 5 estudiantes",
  "datos": [
    {
      "id": 1,
      "numero_documento": "12345678",
      "nombre": "Juan",
      "apellido": "Pérez",
      "email": "juan@example.com",
      "telefono": "3001234567",
      "genero": "Masculino",
      "estado_practica": "Disponible",
      "facultad_id": 1,
      "carrera_id": 1,
      "fecha_creacion": "2026-03-12T10:30:00",
      "fecha_actualizacion": "2026-03-12T10:30:00"
    }
  ]
}
```

### Obtener un estudiante
```
GET /api/estudiantes/{estudiante_id}
```

**Respuesta exitosa (200):**
```json
{
  "datos": {
    "id": 1,
    "numero_documento": "12345678",
    "nombre": "Juan",
    "apellido": "Pérez",
    "email": "juan@example.com",
    "telefono": "3001234567",
    "genero": "Masculino",
    "estado_practica": "Disponible",
    "facultad_id": 1,
    "carrera_id": 1,
    "fecha_creacion": "2026-03-12T10:30:00",
    "fecha_actualizacion": "2026-03-12T10:30:00"
  }
}
```

### Obtener estudiante por documento
```
GET /api/estudiantes/documento/{numero_documento}
```

**Respuesta exitosa (200):**
```json
{
  "datos": { ... }
}
```

### Obtener estudiante por email
```
GET /api/estudiantes/email/{email}
```

**Respuesta exitosa (200):**
```json
{
  "datos": { ... }
}
```

### Crear un estudiante
```
POST /api/estudiantes/
```

**Body JSON requerido:**
```json
{
  "numero_documento": "12345678",
  "nombre": "Juan",
  "apellido": "Pérez",
  "email": "juan@example.com",
  "genero": "Masculino",
  "facultad_id": 1,
  "carrera_id": 1,
  "telefono": "3001234567"
}
```

**Valores válidos para genero:**
- `Masculino`
- `Femenino`
- `Otro`

**Respuesta exitosa (201):**
```json
{
  "mensaje": "Estudiante creado exitosamente",
  "datos": { ... }
}
```

### Actualizar un estudiante
```
PUT /api/estudiantes/{estudiante_id}
```

**Body JSON (campos opcionales):**
```json
{
  "nombre": "Juan Carlos",
  "apellido": "Pérez García",
  "email": "juancarlos@example.com",
  "telefono": "3009876543"
}
```

**Respuesta exitosa (200):**
```json
{
  "mensaje": "Estudiante actualizado exitosamente",
  "datos": { ... }
}
```

### Actualizar estado de práctica
```
PUT /api/estudiantes/{estudiante_id}/estado
```

**Body JSON requerido:**
```json
{
  "estado": "Contratado"
}
```

**Valores válidos para estado:**
- `Disponible`
- `Contratado`
- `Por Finalizar`
- `Finalizó`

**Respuesta exitosa (200):**
```json
{
  "mensaje": "Estado de práctica actualizado exitosamente",
  "datos": { ... }
}
```

### Eliminar un estudiante
```
DELETE /api/estudiantes/{estudiante_id}
```

**Respuesta exitosa (200):**
```json
{
  "mensaje": "Estudiante eliminado exitosamente"
}
```

### Listar estudiantes disponibles
```
GET /api/estudiantes/disponibles
```

**Respuesta exitosa (200):**
```json
{
  "mensaje": "Se encontraron 3 estudiantes disponibles",
  "datos": [ ... ]
}
```

### Estadísticas por facultad
```
GET /api/estudiantes/estadisticas/facultad/{facultad_id}
```

**Respuesta exitosa (200):**
```json
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

### Estadísticas por carrera
```
GET /api/estudiantes/estadisticas/carrera/{carrera_id}
```

**Respuesta exitosa (200):**
```json
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

## Códigos de Estado HTTP

| Código | Descripción |
|--------|-------------|
| 200 | Solicitud exitosa |
| 201 | Recurso creado exitosamente |
| 400 | Solicitud incorrecta / Datos inválidos |
| 404 | Recurso no encontrado |
| 500 | Error interno del servidor |

---

## Ejemplo de Flujo Completo

1. **Crear una facultad:**
```bash
curl -X POST http://localhost:5000/api/facultades/ \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Ingeniería", "descripcion": "Facultad de Ingeniería"}'
```

2. **Crear una carrera en la facultad:**
```bash
curl -X POST http://localhost:5000/api/carreras/ \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Ingeniería de Sistemas", "facultad_id": 1}'
```

3. **Registrar un estudiante:**
```bash
curl -X POST http://localhost:5000/api/estudiantes/ \
  -H "Content-Type: application/json" \
  -d '{
    "numero_documento": "12345678",
    "nombre": "Juan",
    "apellido": "Pérez",
    "email": "juan@example.com",
    "genero": "Masculino",
    "facultad_id": 1,
    "carrera_id": 1,
    "telefono": "3001234567"
  }'
```

4. **Actualizar estado a contratado:**
```bash
curl -X PUT http://localhost:5000/api/estudiantes/1/estado \
  -H "Content-Type: application/json" \
  -d '{"estado": "Contratado"}'
```

5. **Obtener estadísticas:**
```bash
curl http://localhost:5000/api/estudiantes/estadisticas/facultad/1
```
