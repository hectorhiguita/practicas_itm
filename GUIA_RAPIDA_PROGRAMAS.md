# 🚀 GUÍA RÁPIDA - PROGRAMAS ACADÉMICOS

## ⚡ En 5 Minutos

### 1. Cargar datos (Primera vez)
```bash
cd /home/hahiguit/Documents/POC/practicas_itm
python load_programas.py
```
✅ Carga 32 programas en la BD

### 2. Iniciar servidor
```bash
python main.py
```
✅ API disponible en `http://localhost:5000`

### 3. Probar API
```bash
# En otra terminal:
curl http://localhost:5000/api/programas | python -m json.tool
```
✅ Ver todos los programas

---

## 📚 API Endpoints

### Obtener datos

```bash
# Todos los programas
curl http://localhost:5000/api/programas

# Programa específico
curl http://localhost:5000/api/programas/1

# Por nivel
curl 'http://localhost:5000/api/programas/por-nivel/Tecnología'

# Solo acreditados
curl http://localhost:5000/api/programas/acreditados

# Solo virtuales
curl http://localhost:5000/api/programas/virtuales

# Estadísticas
curl http://localhost:5000/api/programas/estadisticas
```

### Crear programa

```bash
curl -X POST http://localhost:5000/api/programas \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Mi Programa",
    "nivel": "Profesional",
    "facultad_id": 1,
    "duracion": "8 semestres",
    "perfil_profesional": "...",
    "acreditada": true
  }'
```

### Actualizar programa

```bash
curl -X PUT http://localhost:5000/api/programas/1 \
  -H "Content-Type: application/json" \
  -d '{"acreditada": true}'
```

### Eliminar programa

```bash
curl -X DELETE http://localhost:5000/api/programas/1
```

---

## 🐍 Uso en Python

### Obtener todos
```python
from src.database.connection import get_session
from src.services.programa_service import ProgramaService

db = get_session()
programas = ProgramaService.obtener_todos_programas(db)
for p in programas:
    print(f"{p.nombre} - {p.nivel}")
db.close()
```

### Buscar por facultad
```python
programas = ProgramaService.obtener_todos_programas(db, facultad_id=1)
```

### Obtener por nivel
```python
tecnologia = ProgramaService.obtener_programas_por_nivel(db, "Tecnología")
```

### Ver acreditados
```python
acreditados = ProgramaService.obtener_programas_acreditados(db)
```

### Crear programa
```python
nuevo = ProgramaService.crear_programa(
    db,
    nombre="Ingeniería de Software",
    nivel="Ingeniería",
    facultad_id=4,
    duracion="10 semestres",
    acreditada=True
)
```

### Estadísticas
```python
stats = ProgramaService.obtener_estadisticas_programas(db)
print(f"Total: {stats['total_programas']}")
print(f"Acreditados: {stats['total_acreditados']}")
```

---

## 📊 Datos Disponibles

### Total
- **32 programas**
- **4 facultades**
- **50% acreditados**
- **6.3% virtuales**

### Distribución
```
Tecnología:    13 programas (40.6%)
Profesional:   10 programas (31.3%)
Ingeniería:     9 programas (28.1%)
```

### Facultades
```
1. Artes y Humanidades                           (6 programas)
2. Ciencias Económicas y Administrativas        (9 programas)
3. Ciencias Exactas y Aplicadas                 (7 programas)
4. Ingenierías                                  (10 programas)
```

---

## 🔧 Archivos Clave

| Archivo | Descripción |
|---------|-------------|
| `load_programas.py` | Cargar datos CSV → BD |
| `demo_programas.py` | Demo interactivo |
| `src/services/programa_service.py` | Lógica de negocio |
| `src/api/routes/programas.py` | Endpoints API |
| `PROGRAMAS_ITM.csv` | Datos de origen |

---

## ⚙️ Configuración

Editar `.env` si necesitas cambiar:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=practicas_itm
DB_USER=hahiguit
APP_PORT=5000
```

---

## 🐛 Troubleshooting

**Error: "Programa no encontrado"**
- Ejecuta: `python load_programas.py`

**Error: "relation carreras does not exist"**
- Ejecuta: `python -c "from src.database.connection import init_db; init_db()"`

**Error: Connection refused**
- ¿PostgreSQL está corriendo?
- Verifica credenciales en `.env`

---

## 📖 Documentación Completa

Ver: `PROGRAMAS_ACADEMICOS_DOCUMENTACION.md`

---

**¡Listo!** 🎉 Tu sistema de programas está en funcionamiento.
