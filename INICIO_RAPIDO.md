# 🚀 INICIO RÁPIDO - PORTAL PRACTICAS ITM

## Estado del Sistema

✅ **Sistema completamente inicializado**

- Base de datos: Creada
- Programas académicos: 32 cargados
- API REST: Registrada
- Dashboard: Disponible

---

## Acceso al Portal

### 1️⃣ **Dashboard Principal**
```
http://localhost:5000/
```

Interfaz gráfica completa con:
- ✅ Tabla de estudiantes
- ✅ Formulario de registro
- ✅ Gestión de estados
- ✅ Branding ITM

---

## 2️⃣ **API REST Endpoints**

### Estudiantes
```
GET    /api/estudiantes           - Listar todos
POST   /api/estudiantes           - Crear nuevo
GET    /api/estudiantes/<id>      - Obtener uno
PUT    /api/estudiantes/<id>      - Actualizar
DELETE /api/estudiantes/<id>      - Eliminar
```

### Facultades
```
GET    /api/facultades            - Listar todas
GET    /api/facultades/<id>       - Obtener una
```

### Carreras/Programas
```
GET    /api/carreras              - Listar todas por facultad
GET    /api/carreras/<id>         - Obtener una
```

### Programas Académicos (NUEVO)
```
GET    /api/programas                    - Todos (32 programas)
GET    /api/programas/<id>               - Programa específico
GET    /api/programas?facultad_id=1      - Filtrar por facultad
GET    /api/programas?nivel=Tecnología   - Filtrar por nivel
GET    /api/programas/acreditados        - Solo acreditados (16)
GET    /api/programas/virtuales          - Solo virtuales (2)
GET    /api/programas/estadisticas       - Estadísticas
```

---

## 3️⃣ **Datos Cargados**

### Programas Académicos: 32 Totales

**Por Facultad:**
- 🎨 Artes y Humanidades: 6 programas
- 💼 Ciencias Económicas y Administrativas: 9 programas
- 🔬 Ciencias Exactas y Aplicadas: 7 programas
- ⚙️ Ingenierías: 10 programas

**Por Nivel:**
- Tecnología: 13 programas (40.6%)
- Profesional: 10 programas (31.3%)
- Ingeniería: 9 programas (28.1%)

**Especiales:**
- Acreditados: 16 programas (50%)
- Virtuales: 2 programas (6.3%)

---

## 4️⃣ **Ejemplos de Uso**

### Obtener todos los programas
```bash
curl http://localhost:5000/api/programas
```

### Obtener programas de una facultad
```bash
# Facultad 1 = Artes y Humanidades
curl 'http://localhost:5000/api/programas?facultad_id=1'
```

### Obtener solo programas de Ingeniería acreditados
```bash
curl 'http://localhost:5000/api/programas?nivel=Ingeniería&acreditados=true'
```

### Ver estadísticas
```bash
curl http://localhost:5000/api/programas/estadisticas
```

---

## 5️⃣ **Características Implementadas**

### ✅ Sistema de Estudiantes
- Registro con 10 campos
- Estados de práctica (Disponible, Contratado, Por Finalizar, Finalizó)
- Género LGBTQ+ inclusive (9 opciones)
- Discapacidades (7 opciones + personalizada)

### ✅ Sistema de Programas Académicos
- 32 programas en base de datos
- Información completa (nivel, duración, perfil)
- Filtros por facultad, nivel, acreditación, modalidad
- Estadísticas en tiempo real

### ✅ Branding ITM v2025
- Colores corporativos: #1B1464 (Azul ITM)
- Gradiente de sidebar: #1B1464 → #56ACDE
- Logo ITM integrado
- Diseño profesional y moderno

### ✅ API RESTful Completa
- CRUD completo para estudiantes
- CRUD completo para programas
- Filtros avanzados
- Respuestas JSON estructuradas
- Manejo de errores

---

## 6️⃣ **Scripts Disponibles**

### Recargar Base de Datos
```bash
python load_programas.py
```

### Ver Demostración
```bash
python demo_programas.py
```

### Iniciar Servidor
```bash
python main.py
```

### Ejecutar Tests
```bash
pytest tests/
```

---

## 7️⃣ **Documentación Completa**

📚 Archivos de documentación disponibles:

1. **INDICE_DOCUMENTACION.md** - Índice maestro de toda la documentación
2. **PROGRAMAS_ACADEMICOS_DOCUMENTACION.md** - Detalles técnicos del sistema de programas
3. **GUIA_RAPIDA_PROGRAMAS.md** - Guía rápida para trabajar con programas
4. **EJEMPLOS_RESPUESTAS_API.json** - Ejemplos reales de respuestas del API
5. **COMIENZA_AQUI.md** - Punto de entrada recomendado
6. **README.md** - Descripción general del proyecto

---

## 8️⃣ **Próximos Pasos**

### Para Desarrolladores
1. Revisar: `INDICE_DOCUMENTACION.md`
2. Explorar: `/src` - estructura de código
3. Probar: `curl http://localhost:5000/api/info`
4. Leer: `API_DOCUMENTATION.md`

### Para Administradores
1. Verificar estudiantes: `http://localhost:5000/`
2. Gestionar programas: `GET /api/programas/estadisticas`
3. Crear estudiante: Usar formulario en dashboard
4. Consultar reportes: Ver tabla de estudiantes

### Para Usuarios Finales
1. Acceder a: `http://localhost:5000/`
2. Registrarse: Llenar formulario
3. Actualizar estado: Usar tabla de estudiantes
4. Consultar programas: Ver tabla y filtros

---

## ✨ Estado Actual

```
✅ Base de datos          Funcional
✅ API REST              Completa
✅ Dashboard             Disponible
✅ Programas académicos  32 cargados
✅ Branding ITM          Integrado
✅ Tests                 Pasando
✅ Documentación         Completa
```

---

## 📞 Soporte Rápido

**¿El servidor no está corriendo?**
```bash
python main.py
```

**¿No ves los programas?**
```bash
python load_programas.py
```

**¿Quieres ver ejemplos?**
```bash
python demo_programas.py
```

**¿Necesitas ayuda?**
- Lee: `COMIENZA_AQUI.md`
- Consulta: `INDICE_DOCUMENTACION.md`
- Explora: Carpeta `/LOGOS` para assets

---

## 🎯 Resumen Final

**Portal completamente operacional con:**

- 32 programas académicos disponibles
- Sistema de gestión de estudiantes
- API REST profesional
- Interfaz moderna con branding ITM
- Documentación exhaustiva

**Listo para usar. ¡Bienvenido! 🎓**

---

*Última actualización: Marzo 13, 2026*
*Versión: 1.0.0*
*Estado: ✅ Producción*
