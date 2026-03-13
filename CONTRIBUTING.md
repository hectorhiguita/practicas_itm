# Guía de Contribución - Practicas ITM

## 🤝 Cómo Contribuir

Gracias por tu interés en contribuir al proyecto. Aquí están las guías para hacer contribuciones efectivas.

## 📋 Requisitos Antes de Contribuir

1. Lee el [README.md](README.md) y la [Guía de Instalación](INSTALL.md)
2. Familiarízate con la [Documentación de la API](API_DOCUMENTATION.md)
3. Comprende la estructura del proyecto

## 🔄 Proceso de Contribución

### 1. Fork del Repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd practicas_itm
```

### 2. Crear una Rama

```bash
git checkout -b feature/nombre-de-la-caracteristica
```

Usa nombres descriptivos para las ramas:
- `feature/nueva-caracteristica` - para nuevas características
- `bugfix/nombre-del-bug` - para corrección de bugs
- `docs/mejora-documentacion` - para cambios en documentación

### 3. Realizar Cambios

- Mantén los cambios enfocados y pequeños
- Sigue las convenciones de código del proyecto
- Actualiza documentación si es necesario

### 4. Escribir Tests

```bash
pytest tests/
```

- Escribe tests para nuevas características
- Asegúrate de que todos los tests pasen

### 5. Commit de Cambios

```bash
git add .
git commit -m "tipo: descripción breve"
```

**Formato de commit:**
- `feat:` Nueva característica
- `fix:` Corrección de bug
- `docs:` Cambios en documentación
- `refactor:` Refactorización de código
- `test:` Adición de tests
- `chore:` Cambios en configuración

**Ejemplos:**
```
feat: agregar filtro por estado en estudiantes
fix: corregir error al obtener estadísticas
docs: actualizar documentación de API
test: agregar tests para CarreraService
```

### 6. Push a tu Fork

```bash
git push origin feature/nombre-de-la-caracteristica
```

### 7. Crear Pull Request

1. Ve al repositorio original
2. Haz clic en "New Pull Request"
3. Selecciona tu rama y describe los cambios
4. Espera a que se revisen tus cambios

## 📝 Estándares de Código

### Python Style Guide (PEP 8)

```python
# ✓ Correcto
def crear_estudiante(db: Session, nombre: str) -> Estudiante:
    """Crea un nuevo estudiante."""
    # Tu código aquí
    pass

# ✗ Incorrecto
def crearEstudiante(db,nombre):
    # Tu código aquí
    pass
```

### Docstrings

Usa docstrings en formato Google:

```python
def crear_estudiante(db: Session, numero_documento: str) -> Estudiante:
    """
    Crea un nuevo estudiante en la base de datos.
    
    Args:
        db: Sesión de base de datos SQLAlchemy
        numero_documento: Número único de documento del estudiante
        
    Returns:
        Estudiante: El estudiante creado
        
    Raises:
        ValueError: Si el documento ya existe
    """
    pass
```

### Type Hints

Usa type hints en funciones:

```python
from typing import List, Optional
from sqlalchemy.orm import Session

def obtener_estudiantes(db: Session, limite: int = 10) -> List[Estudiante]:
    """Obtiene lista de estudiantes."""
    pass
```

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Tests específicos
pytest tests/test_estudiantes.py

# Con cobertura
pytest --cov=src
```

### Escribir Tests

```python
def test_crear_estudiante(db, facultad_test, carrera_test):
    """Prueba la creación de un estudiante."""
    estudiante = EstudianteService.crear_estudiante(
        db=db,
        numero_documento="12345678",
        nombre="Juan",
        apellido="Pérez",
        email="juan@example.com",
        genero="Masculino",
        facultad_id=facultad_test.id,
        carrera_id=carrera_test.id
    )
    
    assert estudiante.id is not None
    assert estudiante.nombre == "Juan"
```

## 📚 Estructura de Carpetas

Mantén la siguiente estructura:

```
src/
├── api/         # Rutas y lógica Flask
├── database/    # Conexión y init de BD
├── models/      # Modelos SQLAlchemy
├── services/    # Lógica de negocio
└── utils/       # Funciones auxiliares
```

## 🐛 Reporte de Bugs

### Título Descriptivo
- Sé específico sobre el problema
- Incluye la acción que causa el error
- Menciona el contexto (SO, versión Python, etc)

### Descripción
1. **Descripción del problema**: Qué está pasando
2. **Pasos para reproducir**: Cómo hacer que ocurra el error
3. **Comportamiento esperado**: Qué debería pasar
4. **Capturas/Logs**: Si es aplicable
5. **Ambiente**: SO, Python, versiones de dependencias

**Ejemplo:**
```
Título: Error al crear estudiante sin email

Descripción:
Cuando intento crear un estudiante sin proporcionar un email,
la aplicación devuelve un error 500 en lugar de un 400.

Pasos:
1. POST /api/estudiantes/
2. Enviar JSON sin campo 'email'
3. Observar error 500

Esperado:
Devolver error 400 con mensaje indicando que email es requerido
```

## 💡 Sugerencias de Características

Abre un Issue con:
1. **Descripción clara** de la característica
2. **Por qué es útil**
3. **Ejemplo de uso** si es aplicable
4. **Consideraciones técnicas**

## 🎯 Checklist Antes de Pull Request

- [ ] Código sigue PEP 8
- [ ] Incluye docstrings
- [ ] Tests escritos y pasando
- [ ] Sin código comentado
- [ ] Sin cambios sin relacionados
- [ ] Mensaje de commit descriptivo
- [ ] Documentación actualizada
- [ ] No hay conflictos con main

## 📖 Recursos Útiles

- [PEP 8 Style Guide](https://pep8.org/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Pytest Guide](https://docs.pytest.org/)

## 🙏 Agradecimientos

¡Gracias por contribuir al proyecto! Tus aportes hacen que esta aplicación sea mejor para todos.

---

**¿Preguntas?** Abre un Issue o contacta a los mantenedores del proyecto.
