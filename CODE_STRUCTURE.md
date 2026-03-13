# 🏗️ Estructura del Código - Practicas ITM

## Descripción General

El proyecto utiliza una **arquitectura en 3 capas** con separación de responsabilidades:

```
API REST (Flask)
    ↓
SERVICIOS (Lógica de Negocio)
    ↓
MODELOS (SQLAlchemy ORM)
    ↓
BASE DE DATOS (PostgreSQL)
```

---

## 1. Capa API REST

### Ubicación: `src/api/`

#### `app.py` - Factory de Flask
```python
def create_app(config=None):
    """Crea y configura la aplicación Flask"""
    app = Flask(__name__)
    app.register_blueprint(estudiantes.bp)
    app.register_blueprint(facultades.bp)
    app.register_blueprint(carreras.bp)
    return app
```

**Responsabilidades:**
- Crear aplicación Flask
- Registrar blueprints
- Configurar middleware
- Manejo de errores HTTP

#### `routes/` - Blueprints con Endpoints

**estudiantes.py** (7 endpoints)
```
GET    /api/estudiantes/
POST   /api/estudiantes/
GET    /api/estudiantes/{id}
PUT    /api/estudiantes/{id}
PUT    /api/estudiantes/{id}/estado
DELETE /api/estudiantes/{id}
GET    /api/estudiantes/disponibles
GET    /api/estudiantes/estadisticas/facultad/{id}
GET    /api/estudiantes/estadisticas/carrera/{id}
GET    /api/estudiantes/documento/{doc}
GET    /api/estudiantes/email/{email}
```

**facultades.py** (5 endpoints)
```
GET    /api/facultades/
POST   /api/facultades/
GET    /api/facultades/{id}
PUT    /api/facultades/{id}
DELETE /api/facultades/{id}
```

**carreras.py** (5 endpoints)
```
GET    /api/carreras/
POST   /api/carreras/
GET    /api/carreras/{id}
PUT    /api/carreras/{id}
DELETE /api/carreras/{id}
```

**Patrón de cada endpoint:**
```python
def operacion(parametros):
    try:
        # Obtener sesión
        db = get_session()
        
        # Llamar servicio
        resultado = Servicio.metodo(db, parametros)
        
        # Cerrar sesión
        db.close()
        
        # Retornar respuesta
        return respuesta_exito(resultado)
    except ValueError as e:
        return respuesta_error(str(e), 400)
    except Exception as e:
        return respuesta_error(f"Error: {e}", 500)
```

---

## 2. Capa de Servicios

### Ubicación: `src/services/`

Los servicios contienen toda la **lógica de negocio** y validaciones.

#### EstudianteService (13 métodos)

```python
class EstudianteService:
    # CRUD
    @staticmethod
    def crear_estudiante(db, numero_documento, nombre, ...):
        """Crear con validaciones"""
        # 1. Validar documento único
        # 2. Validar email único
        # 3. Validar facultad existe
        # 4. Validar carrera existe
        # 5. Crear y guardar

    @staticmethod
    def obtener_estudiante(db, estudiante_id):
        """Obtener por ID"""

    @staticmethod
    def obtener_todos_estudiantes(db):
        """Obtener todos"""

    @staticmethod
    def actualizar_estudiante(db, estudiante_id, ...):
        """Actualizar datos básicos"""

    @staticmethod
    def eliminar_estudiante(db, estudiante_id):
        """Eliminar registro"""

    # BÚSQUEDAS
    @staticmethod
    def obtener_estudiante_por_documento(db, numero_documento):
        """Búsqueda exacta por documento"""

    @staticmethod
    def obtener_estudiante_por_email(db, email):
        """Búsqueda exacta por email"""

    @staticmethod
    def obtener_estudiantes_por_facultad(db, facultad_id):
        """Filtrar por facultad"""

    @staticmethod
    def obtener_estudiantes_por_carrera(db, carrera_id):
        """Filtrar por carrera"""

    @staticmethod
    def obtener_estudiantes_por_estado(db, estado):
        """Filtrar por estado"""

    # ESPECIALIZADOS
    @staticmethod
    def obtener_estudiantes_disponibles(db):
        """Shortcut para obtener disponibles"""

    @staticmethod
    def actualizar_estado_practica(db, estudiante_id, nuevo_estado):
        """Cambiar estado con validaciones"""

    # ESTADÍSTICAS
    @staticmethod
    def obtener_estadisticas_facultad(db, facultad_id):
        """Contar por estado en facultad"""

    @staticmethod
    def obtener_estadisticas_carrera(db, carrera_id):
        """Contar por estado en carrera"""
```

**Características:**
- Métodos `@staticmethod` para usar sin instancia
- Validaciones antes de guardar
- Transacciones automáticas (commit/rollback)
- Retorno de objetos modelo para serialización

#### FacultadService (6 métodos)

```python
class FacultadService:
    @staticmethod
    def crear_facultad(db, nombre, descripcion=None)
    @staticmethod
    def obtener_facultad(db, facultad_id)
    @staticmethod
    def obtener_todas_facultades(db)
    @staticmethod
    def actualizar_facultad(db, facultad_id, nombre=None, descripcion=None)
    @staticmethod
    def eliminar_facultad(db, facultad_id)
```

#### CarreraService (6 métodos)

```python
class CarreraService:
    @staticmethod
    def crear_carrera(db, nombre, facultad_id, descripcion=None)
    @staticmethod
    def obtener_carrera(db, carrera_id)
    @staticmethod
    def obtener_todas_carreras(db)
    @staticmethod
    def obtener_carreras_por_facultad(db, facultad_id)
    @staticmethod
    def actualizar_carrera(db, carrera_id, nombre=None, descripcion=None)
    @staticmethod
    def eliminar_carrera(db, carrera_id)
```

---

## 3. Capa de Modelos

### Ubicación: `src/models/base.py`

Define la estructura de datos con SQLAlchemy ORM.

#### Modelo Facultad

```python
class Facultad(Base):
    __tablename__ = 'facultades'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(255), unique=True, nullable=False)
    descripcion = Column(String(500))
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones 1:N
    carreras = relationship("Carrera", cascade="all, delete-orphan")
    estudiantes = relationship("Estudiante", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convierte a diccionario para JSON"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'fecha_creacion': self.fecha_creacion.isoformat()
        }
```

#### Modelo Carrera

```python
class Carrera(Base):
    __tablename__ = 'carreras'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(String(500))
    facultad_id = Column(Integer, ForeignKey('facultades.id'), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    facultad = relationship("Facultad", back_populates="carreras")
    estudiantes = relationship("Estudiante", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'facultad_id': self.facultad_id,
            'fecha_creacion': self.fecha_creacion.isoformat()
        }
```

#### Modelo Estudiante

```python
class Estudiante(Base):
    __tablename__ = 'estudiantes'
    
    id = Column(Integer, primary_key=True)
    numero_documento = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(255), nullable=False)
    apellido = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    telefono = Column(String(20))
    genero = Column(SQLEnum(Genero), nullable=False)
    estado_practica = Column(SQLEnum(EstadoPractica), default=EstadoPractica.DISPONIBLE)
    facultad_id = Column(Integer, ForeignKey('facultades.id'), nullable=False)
    carrera_id = Column(Integer, ForeignKey('carreras.id'), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    facultad = relationship("Facultad", back_populates="estudiantes")
    carrera = relationship("Carrera", back_populates="estudiantes")
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero_documento': self.numero_documento,
            'nombre': self.nombre,
            # ...más campos
        }
```

---

## 4. Capa de Base de Datos

### Ubicación: `src/database/`

#### connection.py - Gestión de Conexiones

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Crear engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Factory de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session() -> Session:
    """Obtiene una nueva sesión"""
    return SessionLocal()

def test_connection():
    """Prueba conexión"""
    with engine.connect() as connection:
        result = connection.execute("SELECT 1")
        return result.fetchone() is not None
```

**Características:**
- Pool de conexiones (10 conexiones)
- `pool_pre_ping=True` para conexiones vivas
- Sesiones automáticas

#### init_db.py - Inicialización

```python
def create_database():
    """Crea la BD si no existe"""
    # Conecta a postgres por defecto
    # Crea la BD practicas_itm

def init_database():
    """Crea todas las tablas"""
    Base.metadata.create_all(bind=engine)

def main():
    """Ejecuta inicialización completa"""
    create_database()
    init_database()
```

---

## 5. Utilidades

### Ubicación: `src/utils/enums.py`

```python
class EstadoPractica(Enum):
    DISPONIBLE = "Disponible"
    CONTRATADO = "Contratado"
    POR_FINALIZAR = "Por Finalizar"
    FINALIZO = "Finalizó"

class Genero(Enum):
    MASCULINO = "Masculino"
    FEMENINO = "Femenino"
    OTRO = "Otro"
```

**Ventajas:**
- Type safety
- Evita errores de tipeo
- Serialización automática

---

## 6. Configuración

### Ubicación: `src/config.py`

```python
class Config:
    """Configuración base"""
    # Base de datos
    SQLALCHEMY_DATABASE_URI = "postgresql://user:pass@host:5432/db"
    
    # Flask
    SECRET_KEY = "secret"
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    DB_NAME = "practicas_itm_test"
```

---

## 7. Testing

### Ubicación: `tests/`

#### test_estudiantes.py

```python
@pytest.fixture
def db():
    """Crea BD temporal para cada test"""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_crear_estudiante(db, facultad_test, carrera_test):
    """Test del servicio"""
    estudiante = EstudianteService.crear_estudiante(...)
    assert estudiante.id is not None
    assert estudiante.estado_practica == EstadoPractica.DISPONIBLE
```

**Patrón:**
1. Setup (crear fixtures)
2. Acción (llamar función)
3. Aserción (verificar resultado)
4. Teardown (limpiar)

---

## 8. Flujo de una Solicitud

```
1. Cliente HTTP (curl, browser, api_client.py)
   │
   └─→ POST /api/estudiantes/ + JSON
       │
       2. Flask Router (app.py)
          │ Recibe request
          │ Parsea JSON
          │
          └─→ Endpoint: crear_estudiante()
              │ Valida JSON
              │
              3. Services (EstudianteService)
                 │ crear_estudiante(db, datos...)
                 │ ├─ Validar documento único
                 │ ├─ Validar email único
                 │ ├─ Validar facultad existe
                 │ ├─ Validar carrera existe
                 │
                 4. Models (SQLAlchemy)
                    │ Crear objeto Estudiante()
                    │
                    5. Database (PostgreSQL)
                       │ INSERT INTO estudiantes
                       │ RETURNING id, ...
                       │
                    ├─ Retorna objeto Estudiante
                 │
                 └─ Retorna Estudiante objeto
              │
              └─ Serializa a JSON (to_dict())
          │
          └─→ respuesta_exito(datos)
       │
       └─→ 201 Created + JSON
           │
           └─ Cliente recibe respuesta
```

---

## 9. Patrón de Validaciones

```python
def crear_estudiante(db, numero_documento, nombre, ...):
    # 1. Validación de duplicados
    existente = db.query(Estudiante).filter(
        Estudiante.numero_documento == numero_documento
    ).first()
    if existente:
        raise ValueError("Documento ya existe")
    
    # 2. Validación de referencias
    facultad = db.query(Facultad).filter(
        Facultad.id == facultad_id
    ).first()
    if not facultad:
        raise ValueError("Facultad no existe")
    
    # 3. Validación de enums
    try:
        genero_enum = Genero[genero.upper()]
    except KeyError:
        raise ValueError("Género inválido")
    
    # 4. Crear y guardar
    estudiante = Estudiante(
        numero_documento=numero_documento,
        nombre=nombre,
        genero=genero_enum,
        # ...
    )
    db.add(estudiante)
    db.commit()
    db.refresh(estudiante)
    return estudiante
```

---

## 10. Principios de Diseño

### Separación de Responsabilidades
- **API**: Solo HTTP
- **Services**: Lógica de negocio
- **Models**: Estructura de datos
- **Database**: Persistencia

### DRY (Don't Repeat Yourself)
- Métodos reutilizables en Services
- Fixtures reutilizables en Tests
- Configuración centralizada

### SOLID
- **Single Responsibility**: Cada clase hace una cosa
- **Open/Closed**: Fácil extender, difícil modificar
- **Liskov**: Herencia correcta
- **Interface Segregation**: Interfaces pequeñas
- **Dependency Inversion**: Inyección de dependencias

---

## 11. Extensiones Futuras

### Agregar Nueva Entidad (Ejemplo: Empresa)

1. **Crear modelo** en `models/base.py`
```python
class Empresa(Base):
    __tablename__ = 'empresas'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(255), nullable=False)
    # ...
```

2. **Crear servicio** en `services/empresa_service.py`
```python
class EmpresaService:
    @staticmethod
    def crear_empresa(db, nombre, ...):
        # lógica
```

3. **Crear rutas** en `api/routes/empresas.py`
```python
@bp.route('/', methods=['POST'])
def crear_empresa():
    # endpoint
```

4. **Registrar blueprint** en `api/app.py`
```python
app.register_blueprint(empresas.bp)
```

5. **Escribir tests** en `tests/test_empresas.py`

---

**Última actualización:** Marzo 12, 2026  
**Versión:** 1.0.0
