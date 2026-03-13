# Changelog - Practicas ITM

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [1.0.0] - 2026-03-12

### Added
- Módulo de gestión de estudiantes completo
- Módulo de gestión de facultades
- Módulo de gestión de carreras
- API REST con Flask con endpoints CRUD
- Estados de práctica: Disponible, Contratado, Por Finalizar, Finalizó
- Segmentación por facultad y carrera
- Base de datos PostgreSQL con SQLAlchemy ORM
- Sistema de filtros y búsquedas
- Estadísticas por facultad y carrera
- Tests unitarios e integración
- Documentación completa de API
- Guía de instalación
- Docker y Docker Compose
- Script de inicialización de base de datos
- Script de poblamiento de datos de ejemplo
- Sistema de configuración por entorno
- Validaciones de datos
- Gestión de errores

### Features Principales
- ✅ CRUD completo para Estudiantes
- ✅ CRUD completo para Facultades
- ✅ CRUD completo para Carreras
- ✅ Búsqueda y filtrado de estudiantes
- ✅ Control de estados de práctica
- ✅ Reportes y estadísticas
- ✅ API REST documentada
- ✅ Base de datos relacional
- ✅ Tests automatizados
- ✅ Docker para facilitar deploy

## [Próximamente]

### Planned Features
- [ ] Autenticación y autorización (JWT)
- [ ] Módulo de empresas
- [ ] Módulo de asesores de prácticas
- [ ] Asignación automática de prácticas
- [ ] Sistema de notificaciones
- [ ] Panel de administración (Web Dashboard)
- [ ] Reportes avanzados (PDF, Excel)
- [ ] Historial de cambios
- [ ] Auditoría de acciones
- [ ] API GraphQL
- [ ] Cache con Redis
- [ ] Paginación mejorada
- [ ] Búsqueda full-text
- [ ] Integración con email
- [ ] Sistema de permisos granulares

---

## Notas de Versión

### Versión 1.0.0
Primera versión funcional del sistema de gestión de prácticas con:
- Estructura modular y escalable
- API REST completa
- Base de datos robusta
- Documentación extensiva
- Tests unitarios
- Fácil deploy con Docker

---

## Versionamiento

Este proyecto sigue [Semantic Versioning](https://semver.org/):
- **MAJOR**: Cambios incompatibles en la API
- **MINOR**: Nuevas características compatibles
- **PATCH**: Correcciones de bugs

**Formato:** X.Y.Z (ej: 1.0.0)

---

Para más información, consulta:
- [README](README.md)
- [API Documentation](API_DOCUMENTATION.md)
- [Guía de Instalación](INSTALL.md)
