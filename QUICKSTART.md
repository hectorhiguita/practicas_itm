# 🚀 QUICK START - Guía Rápida

## 1️⃣ Instalación en 5 minutos

### Opción A: Docker (Más fácil)
```bash
git clone <repo>
cd practicas_itm
docker-compose up
# Acceder a http://localhost:5000
```

### Opción B: Manual
```bash
git clone <repo>
cd practicas_itm
pip install -r requirements.txt
cp .env.example .env
# Editar .env si es necesario (PostgreSQL)
python -m src.database.init_db
python seed_db.py  # Datos de ejemplo
python main.py
```

### Opción C: Con Make
```bash
git clone <repo>
cd practicas_itm
make setup
make run
```

---

## 2️⃣ Primeros Pasos

### Ver estado de la API
```bash
curl http://localhost:5000/api/health
```

### Crear una Facultad
```bash
curl -X POST http://localhost:5000/api/facultades/ \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Ingeniería","descripcion":"Facultad de Ingeniería"}'
```

### Crear una Carrera
```bash
curl -X POST http://localhost:5000/api/carreras/ \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Ing. Sistemas","facultad_id":1,"descripcion":"Sistemas"}'
```

### Registrar un Estudiante
```bash
curl -X POST http://localhost:5000/api/estudiantes/ \
  -H "Content-Type: application/json" \
  -d '{
    "numero_documento":"12345678",
    "nombre":"Juan",
    "apellido":"Pérez",
    "email":"juan@example.com",
    "genero":"Masculino",
    "facultad_id":1,
    "carrera_id":1,
    "telefono":"3001234567"
  }'
```

### Ver Estudiantes Disponibles
```bash
curl http://localhost:5000/api/estudiantes/disponibles
```

### Cambiar Estado de Estudiante
```bash
curl -X PUT http://localhost:5000/api/estudiantes/1/estado \
  -H "Content-Type: application/json" \
  -d '{"estado":"Contratado"}'
```

---

## 3️⃣ Comandos Útiles

### Inicializar BD desde cero
```bash
# Opción 1
python -m src.database.init_db

# Opción 2
make db-init

# Opción 3
bash dev.sh db-init
```

### Ejecutar Tests
```bash
# Simple
pytest

# Con cobertura
pytest --cov=src

# Específico
pytest tests/test_estudiantes.py -v
```

### Poblar BD con datos de ejemplo
```bash
python seed_db.py
```

### Usar cliente API CLI
```bash
python api_client.py help
python api_client.py listar-facultades
python api_client.py crear-estudiante "12345" "Juan" "Pérez" "juan@email.com" "Masculino" 1 1 "3001234567"
```

---

## 4️⃣ Estados de Práctica

| Estado | Significado | Código |
|--------|-----------|--------|
| Disponible | Listo para ser contratado | `"Disponible"` |
| Contratado | En práctica en empresa | `"Contratado"` |
| Por Finalizar | Finalizando práctica | `"Por Finalizar"` |
| Finalizó | Práctica completada | `"Finalizó"` |

---

## 5️⃣ Valores Válidos

### Géneros
```
"Masculino", "Femenino", "Otro"
```

### Estados
```
"Disponible", "Contratado", "Por Finalizar", "Finalizó"
```

---

## 6️⃣ Endpoints Principales

### Estudiantes
| Método | Endpoint | Descripción |
|--------|----------|------------|
| GET | `/api/estudiantes/` | Listar (con filtros) |
| POST | `/api/estudiantes/` | Crear |
| GET | `/api/estudiantes/{id}` | Obtener |
| PUT | `/api/estudiantes/{id}` | Actualizar datos |
| PUT | `/api/estudiantes/{id}/estado` | Cambiar estado |
| DELETE | `/api/estudiantes/{id}` | Eliminar |
| GET | `/api/estudiantes/disponibles` | Ver disponibles |
| GET | `/api/estudiantes/estadisticas/facultad/{id}` | Estadísticas |

### Facultades
| Método | Endpoint | Descripción |
|--------|----------|------------|
| GET | `/api/facultades/` | Listar |
| POST | `/api/facultades/` | Crear |
| GET | `/api/facultades/{id}` | Obtener |
| PUT | `/api/facultades/{id}` | Actualizar |
| DELETE | `/api/facultades/{id}` | Eliminar |

### Carreras
| Método | Endpoint | Descripción |
|--------|----------|------------|
| GET | `/api/carreras/` | Listar |
| POST | `/api/carreras/` | Crear |
| GET | `/api/carreras/{id}` | Obtener |
| PUT | `/api/carreras/{id}` | Actualizar |
| DELETE | `/api/carreras/{id}` | Eliminar |

---

## 7️⃣ Filtros Disponibles

### Listar Estudiantes
```bash
# Por facultad
curl http://localhost:5000/api/estudiantes?facultad_id=1

# Por carrera
curl http://localhost:5000/api/estudiantes?carrera_id=1

# Por estado
curl http://localhost:5000/api/estudiantes?estado=disponible

# Por documento
curl http://localhost:5000/api/estudiantes/documento/12345678

# Por email
curl http://localhost:5000/api/estudiantes/email/juan@example.com
```

### Listar Carreras
```bash
# Por facultad
curl http://localhost:5000/api/carreras?facultad_id=1
```

---

## 8️⃣ Solución de Problemas

### Error de conexión a BD
```bash
# Verificar que PostgreSQL está corriendo
psql -U postgres

# O con Docker
docker-compose up postgres
```

### Puerto 5000 ocupado
```bash
# Cambiar puerto en .env
APP_PORT=5001

# Y reiniciar
python main.py
```

### Dependencias no instaladas
```bash
pip install -r requirements.txt
```

### Quitar BD y empezar de cero
```bash
make db-reset
# o
python -c "from src.database.connection import engine; from src.models.base import Base; Base.metadata.drop_all(bind=engine)"
python -m src.database.init_db
python seed_db.py
```

---

## 9️⃣ Ejemplos Completos

### Flujo completo: Crear facultad → Carrera → Estudiante

```bash
# 1. Crear facultad
FACULTAD=$(curl -s -X POST http://localhost:5000/api/facultades/ \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Ingeniería","descripcion":"Fac. de Ingeniería"}' | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*')

echo "Facultad creada con ID: $FACULTAD"

# 2. Crear carrera
CARRERA=$(curl -s -X POST http://localhost:5000/api/carreras/ \
  -H "Content-Type: application/json" \
  -d "{\"nombre\":\"Ing. Sistemas\",\"facultad_id\":$FACULTAD}" | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*')

echo "Carrera creada con ID: $CARRERA"

# 3. Crear estudiante
ESTUDIANTE=$(curl -s -X POST http://localhost:5000/api/estudiantes/ \
  -H "Content-Type: application/json" \
  -d "{\"numero_documento\":\"12345678\",\"nombre\":\"Juan\",\"apellido\":\"Pérez\",\"email\":\"juan@example.com\",\"genero\":\"Masculino\",\"facultad_id\":$FACULTAD,\"carrera_id\":$CARRERA}" | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*')

echo "Estudiante creado con ID: $ESTUDIANTE"

# 4. Cambiar estado
curl -X PUT http://localhost:5000/api/estudiantes/$ESTUDIANTE/estado \
  -H "Content-Type: application/json" \
  -d '{"estado":"Contratado"}'

# 5. Ver estadísticas
curl http://localhost:5000/api/estudiantes/estadisticas/facultad/$FACULTAD
```

---

## 🔟 Documentación Completa

- 📖 [Guía de Instalación](INSTALL.md)
- 🔌 [API Documentation](API_DOCUMENTATION.md)
- 🤝 [Contributing](CONTRIBUTING.md)
- 📊 [Project Summary](PROJECT_SUMMARY.md)

---

## ✅ Checklist de Primeros Pasos

- [ ] ✅ Clonar repositorio
- [ ] ✅ Instalar dependencias
- [ ] ✅ Configurar `.env`
- [ ] ✅ Inicializar BD
- [ ] ✅ Ejecutar servidor
- [ ] ✅ Hacer primer request
- [ ] ✅ Crear facultad
- [ ] ✅ Crear carrera
- [ ] ✅ Crear estudiante
- [ ] ✅ Cambiar estado
- [ ] ✅ Ver estadísticas

---

**¡Listo! Ahora puedes usar el sistema.** 🎉

Para más información: [README.md](README.md)
