# 🎓 Practicas ITM - Sistema de Gestión de Prácticas Universitarias

Sistema modular en Python para gestionar prácticas estudiantiles, facultades, carreras y estudiantes en una universidad.

## ✨ Características Principales

- ✅ **Módulo de Estudiantes**: CRUD completo con 4 estados de práctica
- ✅ **Módulo de Facultades**: Gestión de facultades y carreras
- ✅ **API REST**: 17+ endpoints con filtros avanzados
- ✅ **Base de Datos**: PostgreSQL con relaciones bien definidas
- ✅ **Tests**: Suite de tests unitarios e integración
- ✅ **Docker**: Deployment fácil con Docker Compose
- ✅ **Documentación**: Completa con ejemplos y guías

## 🚀 Inicio Rápido

### Con Docker (Recomendado)
```bash
docker-compose up
```

### Sin Docker
```bash
# 1. Clonar
git clone <repositorio>
cd practicas_itm

# 2. Instalar
pip install -r requirements.txt

# 3. Configurar
cp .env.example .env
# Editar .env con credenciales PostgreSQL

# 4. Inicializar BD
python -m src.database.init_db

# 5. Ejecutar
python main.py
```

## 📚 Documentación

- 📖 [Guía de Instalación Detallada](INSTALL.md)
- 🔌 [Referencia Completa de API](API_DOCUMENTATION.md)
- 🛠️ [Guía de Contribución](CONTRIBUTING.md)
- 📝 [Historial de Cambios](CHANGELOG.md)
- 📊 [Resumen del Proyecto](PROJECT_SUMMARY.md)

## 📊 Estados de Práctica

```
Disponible (🟢) → Contratado (🟡) → Por Finalizar (🔴) → Finalizó (⚫)
```

## 🏗️ Arquitectura

```
API REST (Flask)
    ↓
Services (Lógica de negocio)
    ↓
Models (SQLAlchemy ORM)
    ↓
PostgreSQL (Base de Datos)
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=src

# Tests específicos
pytest tests/test_estudiantes.py -v
```

## 🛠️ Herramientas Útiles

```bash
# Con Make
make help          # Ver comandos disponibles
make setup         # Setup inicial completo
make run           # Ejecutar servidor
make test          # Ejecutar tests
make db-reset      # Reiniciar BD

# Con Script
bash dev.sh help   # Ver comandos de desarrollo

# Cliente API
python api_client.py help  # Cliente CLI para pruebas
```

## 📱 Ejemplo de Uso

```bash
# Crear una facultad
curl -X POST http://localhost:5000/api/facultades/ \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Ingeniería","descripcion":"Facultad de Ingeniería"}'

# Crear un estudiante
curl -X POST http://localhost:5000/api/estudiantes/ \
  -H "Content-Type: application/json" \
  -d '{
    "numero_documento":"12345678",
    "nombre":"Juan",
    "apellido":"Pérez",
    "email":"juan@example.com",
    "genero":"Masculino",
    "facultad_id":1,
    "carrera_id":1
  }'

# Cambiar estado a "Contratado"
curl -X PUT http://localhost:5000/api/estudiantes/1/estado \
  -H "Content-Type: application/json" \
  -d '{"estado":"Contratado"}'
```

## 🐍 Tecnologías

| Componente | Tecnología |
|-----------|-----------|
| Backend | Python 3.8+ |
| API | Flask 3.0 |
| ORM | SQLAlchemy 2.0 |
| BD | PostgreSQL 12+ |
| Testing | Pytest |
| Container | Docker |

## 📋 Requisitos

- Python 3.8+
- PostgreSQL 12+
- Docker (opcional)

## 📁 Estructura

```
practicas_itm/
├── src/              # Código fuente
│   ├── api/         # API REST
│   ├── database/    # BD
│   ├── models/      # Modelos
│   ├── services/    # Lógica
│   └── utils/       # Utilidades
├── tests/           # Tests
├── docker-compose.yml
├── Dockerfile
├── main.py          # Punto de entrada
└── requirements.txt # Dependencias
```

## 🎯 Endpoints Principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/estudiantes/` | Listar estudiantes |
| POST | `/api/estudiantes/` | Crear estudiante |
| PUT | `/api/estudiantes/{id}/estado` | Cambiar estado |
| GET | `/api/estudiantes/disponibles` | Ver disponibles |
| GET | `/api/facultades/` | Listar facultades |
| POST | `/api/facultades/` | Crear facultad |

[Ver más endpoints →](API_DOCUMENTATION.md)

## 🔄 Próximas Fases

- [ ] Autenticación JWT
- [ ] Módulo de Empresas
- [ ] Módulo de Asesores
- [ ] Dashboard Web
- [ ] Reportes PDF/Excel
- [ ] Notificaciones por Email

## 🤝 Contribuir

Ver [Guía de Contribución](CONTRIBUTING.md)

## 📄 Licencia

MIT License - Ver archivo [LICENSE](LICENSE)

---

**¿Necesitas ayuda?** Consulta la [documentación completa](INSTALL.md) o abre un Issue en el repositorio.
