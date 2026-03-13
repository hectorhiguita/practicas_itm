# 🎓 PRACTICAS ITM - GUÍA RÁPIDA DE USO

## ✅ El Portal Está Completamente Operacional

**URL Principal:** http://localhost:5000/

---

## 📊 Datos Disponibles

- **32 programas académicos** cargados en la base de datos
- **4 facultades** completamente configuradas
- **16 programas acreditados** (50%)
- **2 programas virtuales** (6.3%)
- **3 niveles** de educación: Tecnología, Profesional, Ingeniería

---

## 🚀 3 Formas de Usar el Sistema

### 1️⃣ Interfaz Web (Recomendado para usuarios)
```
Accede a: http://localhost:5000/
- Registra estudiantes
- Gestiona estados de práctica
- Visualiza tabla de estudiantes
```

### 2️⃣ API REST (Para desarrolladores)
```bash
# Listar todos los programas
curl http://localhost:5000/api/programas

# Ver estadísticas
curl http://localhost:5000/api/programas/estadisticas

# Filtrar por facultad
curl 'http://localhost:5000/api/programas?facultad_id=1'
```

### 3️⃣ Base de Datos Directa (Para administradores)
```bash
# Conectarse a PostgreSQL
psycopg2 postgresql://usuario:pass@localhost/practicas_itm

# Consultar programas
SELECT COUNT(*) FROM carreras;
```

---

## 📋 Formatos de Datos

### Estudiante (10 campos)
```json
{
  "numero_documento": "123456789",
  "nombre": "Juan",
  "apellido": "Pérez",
  "email": "juan@email.com",
  "telefono": "3001234567",
  "genero": "Masculino",
  "facultad_id": 1,
  "carrera_id": 1,
  "tiene_discapacidad": "No",
  "estado_practica": "Disponible"
}
```

### Programa Académico
```json
{
  "id": 1,
  "nombre": "Ingeniería de Sistemas",
  "nivel": "Ingeniería",
  "duracion": "10 semestres",
  "perfil_profesional": "...",
  "acreditada": true,
  "virtual": false,
  "facultad_id": 4
}
```

---

## 📡 Endpoints Principales

### Programas Académicos
```
GET    /api/programas                    Listar todos (32)
GET    /api/programas/<id>               Obtener uno
GET    /api/programas?facultad_id=1      Filtrar por facultad
GET    /api/programas?nivel=Ingeniería   Filtrar por nivel
GET    /api/programas/acreditados        Solo acreditados (16)
GET    /api/programas/virtuales          Solo virtuales (2)
GET    /api/programas/estadisticas       Estadísticas
POST   /api/programas                    Crear nuevo
PUT    /api/programas/<id>               Actualizar
DELETE /api/programas/<id>               Eliminar
```

### Estudiantes
```
GET    /api/estudiantes                  Listar todos
POST   /api/estudiantes                  Crear nuevo
GET    /api/estudiantes/<id>             Obtener uno
PUT    /api/estudiantes/<id>             Actualizar
DELETE /api/estudiantes/<id>             Eliminar
```

### Otros
```
GET    /api/health                       Verificar salud
GET    /api/info                         Información API
GET    /api/facultades                   Listar facultades
GET    /api/carreras                     Listar carreras
```

---

## 🎯 Casos de Uso Comunes

### 1. Registrar un Estudiante
```bash
curl -X POST http://localhost:5000/api/estudiantes \
  -H "Content-Type: application/json" \
  -d '{
    "numero_documento": "123456",
    "nombre": "Carlos",
    "apellido": "Gómez",
    "email": "carlos@email.com",
    "telefono": "3001234567",
    "genero": "Masculino",
    "facultad_id": 1,
    "carrera_id": 1,
    "tiene_discapacidad": "No"
  }'
```

### 2. Ver Programas de una Facultad
```bash
# Facultad 1 = Artes y Humanidades
curl 'http://localhost:5000/api/programas?facultad_id=1'
```

### 3. Ver Solo Programas Acreditados
```bash
curl http://localhost:5000/api/programas/acreditados
```

### 4. Cambiar Estado de Estudiante
```bash
curl -X PUT http://localhost:5000/api/estudiantes/1 \
  -H "Content-Type: application/json" \
  -d '{"estado_practica": "Contratado"}'
```

### 5. Ver Estadísticas
```bash
curl http://localhost:5000/api/programas/estadisticas
```

---

## 🎨 Facultades Disponibles

1. **Artes y Humanidades** (6 programas)
2. **Ciencias Económicas y Administrativas** (9 programas)
3. **Ciencias Exactas y Aplicadas** (7 programas)
4. **Ingenierías** (10 programas)

---

## 💡 Tips Útiles

1. **Copiar ID de facultad:** Usa el número 1-4 en los filtros
2. **Programas virtuales:** Solo 2 disponibles (ID en estadísticas)
3. **Documentación:** Lee PROGRAMAS_ACADEMICOS_DOCUMENTACION.md
4. **Ejemplos:** Ver EJEMPLOS_RESPUESTAS_API.json
5. **Ayuda:** Consult INICIO_RAPIDO.md

---

## 🔍 Respuesta de Ejemplo - Estadísticas

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

## ⚙️ Configuración

**Base de datos:** PostgreSQL (practicas_itm)
**Host:** localhost
**Puerto API:** 5000
**Zona horaria:** America/Bogota
**Charset:** UTF-8

---

## 📞 Soporte Rápido

| Problema | Solución |
|----------|----------|
| Portal no carga | Verifica http://localhost:5000/ |
| API retorna error | Consulta /api/health |
| Programas no se ven | Ejecuta `python load_programas.py` |
| No sabes qué hacer | Lee INICIO_RAPIDO.md |
| Necesitas ejemplos | Ver EJEMPLOS_RESPUESTAS_API.json |

---

## 🎊 ¡Listo para Usar!

El portal está completamente operacional. 

**Comienza accediendo a:** http://localhost:5000/

---

**Última actualización:** Marzo 13, 2026
**Versión:** 1.0.0
**Estado:** ✅ Producción
