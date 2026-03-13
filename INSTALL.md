# Guía de Instalación y Uso - Practicas ITM

## 📋 Requisitos Previos

- **Python 3.8+** - [Descargar](https://www.python.org/downloads/)
- **PostgreSQL 12+** - [Descargar](https://www.postgresql.org/download/)
- **pip** - Viene incluido con Python
- **Git** (opcional) - Para clonar el repositorio

## 🚀 Instalación Rápida

### Paso 1: Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd practicas_itm
```

### Paso 2: Crear entorno virtual

#### En Linux/Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### En Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### Paso 3: Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Configurar variables de entorno

Copiar el archivo de ejemplo:
```bash
cp .env.example .env
```

Editar el archivo `.env` con tus credenciales de PostgreSQL:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=practicas_itm
DB_USER=tu_usuario_postgres
DB_PASSWORD=tu_contraseña_postgres
```

### Paso 5: Crear la base de datos

```bash
python -m src.database.init_db
```

Este comando:
1. Conecta a PostgreSQL
2. Crea la base de datos `practicas_itm` si no existe
3. Crea todas las tablas necesarias

### Paso 6: Poblar datos de ejemplo (opcional)

```bash
python seed_db.py
```

Esto crea:
- 3 Facultades
- 5 Carreras
- 6 Estudiantes con diferentes estados

## 🎯 Uso de la Aplicación

### Iniciar el servidor

```bash
python main.py
```

Deberías ver:
```
============================================================
Practicas ITM - Sistema de Gestión de Prácticas
============================================================
Ambiente: development
Debug: True
Host: 0.0.0.0
Puerto: 5000
Base de datos: practicas_itm
============================================================
Iniciando servidor...
============================================================
```

### Acceder a la API

Abre tu navegador en:
```
http://localhost:5000
```

O usa `curl`:
```bash
curl http://localhost:5000/api/health
```

## 📚 Ejemplos de Uso

### 1. Crear una Facultad

```bash
curl -X POST http://localhost:5000/api/facultades/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Ingeniería",
    "descripcion": "Facultad de Ingeniería"
  }'
```

**Respuesta (201):**
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

### 2. Crear una Carrera

```bash
curl -X POST http://localhost:5000/api/carreras/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Ingeniería de Sistemas",
    "facultad_id": 1,
    "descripcion": "Carrera de Ingeniería de Sistemas"
  }'
```

### 3. Registrar un Estudiante

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

### 4. Listar Estudiantes Disponibles

```bash
curl http://localhost:5000/api/estudiantes/disponibles
```

### 5. Actualizar Estado de Práctica

```bash
curl -X PUT http://localhost:5000/api/estudiantes/1/estado \
  -H "Content-Type: application/json" \
  -d '{"estado": "Contratado"}'
```

### 6. Obtener Estadísticas por Facultad

```bash
curl http://localhost:5000/api/estudiantes/estadisticas/facultad/1
```

**Respuesta:**
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

## 🧪 Ejecutar Tests

```bash
# Ejecutar todos los tests
pytest

# Ejecutar tests con cobertura
pytest --cov=src

# Ejecutar tests específicos
pytest tests/test_estudiantes.py -v
```

## 📁 Estructura de Directorios

```
practicas_itm/
├── src/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── estudiantes.py
│   │   │   ├── facultades.py
│   │   │   └── carreras.py
│   │   └── app.py
│   ├── database/
│   │   ├── connection.py
│   │   └── init_db.py
│   ├── models/
│   │   └── base.py
│   ├── services/
│   │   ├── estudiante_service.py
│   │   ├── facultad_service.py
│   │   └── carrera_service.py
│   ├── utils/
│   │   └── enums.py
│   └── config.py
├── tests/
│   ├── test_api.py
│   ├── test_database.py
│   └── test_estudiantes.py
├── .env
├── .env.example
├── .gitignore
├── API_DOCUMENTATION.md
├── INSTALL.md (este archivo)
├── README.md
├── requirements.txt
├── main.py
└── seed_db.py
```

## 🐛 Solución de Problemas

### Error: "Could not connect to database"

**Problema:** PostgreSQL no está corriendo o las credenciales son incorrectas

**Solución:**
1. Verificar que PostgreSQL está ejecutándose
2. Confirmar credenciales en `.env`
3. En Linux: `sudo service postgresql start`
4. En Mac: `brew services start postgresql`

### Error: "ModuleNotFoundError"

**Problema:** Las dependencias no están instaladas

**Solución:**
```bash
pip install -r requirements.txt
```

### Error: "Database does not exist"

**Problema:** La base de datos no ha sido creada

**Solución:**
```bash
python -m src.database.init_db
```

### Puerto 5000 ya está en uso

**Problema:** El puerto 5000 está siendo utilizado por otra aplicación

**Solución:** Cambiar el puerto en `.env`:
```
APP_PORT=5001
```

## 🔑 Valores Válidos

### Estados de Práctica
- `Disponible` - El estudiante está disponible
- `Contratado` - El estudiante fue contratado
- `Por Finalizar` - La práctica está por finalizar
- `Finalizó` - La práctica fue finalizada

### Géneros
- `Masculino`
- `Femenino`
- `Otro`

## 📖 Documentación Completa

Para más detalles sobre los endpoints de la API, consulta:
- [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)

## 💡 Tips

- Siempre crea las **Facultades** antes de las **Carreras**
- Las **Carreras** deben estar asociadas a una **Facultad**
- Los **Estudiantes** deben estar asociados a una **Facultad** y **Carrera**
- Puedes filtrar estudiantes por `facultad_id`, `carrera_id` o `estado`

## 📞 Soporte

Para reportar bugs o sugerencias, crea un issue en el repositorio.

## 📄 Licencia

Este proyecto está bajo licencia MIT. Ver archivo `LICENSE` para más detalles.

---

**¡Listo! Tu sistema de gestión de prácticas está correctamente configurado y listo para usar.** 🎉
