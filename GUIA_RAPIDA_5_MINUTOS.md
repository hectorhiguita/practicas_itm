# 🚀 Guía Rápida de 5 Minutos - Practicas ITM

## 1️⃣ Iniciar el Servidor (30 segundos)

```bash
cd /home/hahiguit/Documents/POC/practicas_itm
/home/hahiguit/Documents/POC/practicas_itm/.venv/bin/python main.py
```

O usando el script:
```bash
./run_server.sh
```

**Resultado esperado:**
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
 * Running on http://127.0.0.1:5000
```

---

## 2️⃣ Abrir el Dashboard (10 segundos)

Abre tu navegador y ve a:
```
http://localhost:5000
```

**Deberías ver:**
- Logo "Practicas ITM" a la izquierda
- Menú con 4 opciones: Dashboard, Estudiantes, Carreras, Facultades
- Panel de estadísticas en la parte principal

---

## 3️⃣ Crear tu Primera Facultad (2 minutos)

1. Haz clic en "**Facultades**" en el menú izquierdo
2. Haz clic en el botón "**+ Agregar**" (arriba a la derecha)
3. Completa:
   - **Nombre**: `Ingeniería`
   - **Descripción**: `Facultad de Ingeniería`
4. Haz clic en "**Guardar**"
5. ✅ ¡Facultad creada!

---

## 4️⃣ Crear tu Primer Programa (1.5 minutos)

1. Haz clic en "**Carreras**" en el menú
2. Haz clic en "**+ Agregar**"
3. Completa:
   - **Nombre**: `Ingeniería de Sistemas`
   - **Facultad**: Selecciona `Ingeniería` (que creaste)
   - **Descripción**: `Programa de Ingeniería de Sistemas`
4. Haz clic en "**Guardar**"
5. ✅ ¡Carrera creada!

---

## 5️⃣ Registrar tu Primer Estudiante (1.5 minutos)

1. Haz clic en "**Estudiantes**" en el menú
2. Haz clic en "**+ Agregar**"
3. Completa los campos requeridos (*):
   - **Documento**: `1001234567`
   - **Nombre**: `Juan`
   - **Apellido**: `Pérez`
   - **Email**: `juan@example.com`
   - **Teléfono**: `3001234567`
   - **Género**: Selecciona una opción
   - **Facultad**: `Ingeniería`
   - **Carrera**: `Ingeniería de Sistemas` (se filtra automáticamente)

4. **Opcional** - Discapacidad:
   - Si selecciona "Otra", aparece un campo para especificar

5. Haz clic en "**Guardar**"
6. ✅ ¡Estudiante registrado!

---

## 6️⃣ Ver Estadísticas en Tiempo Real (30 segundos)

1. Haz clic en "**Dashboard**" en el menú
2. Verás automáticamente:
   - Total de estudiantes: 1
   - Disponibles: 1
   - Y más estadísticas...

---

## 🔍 Pruebas Rápidas Adicionales

### Buscar un Estudiante
1. En "Estudiantes", usa el buscador superior
2. Escribe el nombre, documento o email
3. ✅ Se filtra automáticamente

### Filtrar por Estado
1. En "Estudiantes", usa el dropdown "Todos los estados"
2. Selecciona "Disponible"
3. ✅ Se muestran solo estudiantes disponibles

### Editar un Estudiante
1. En "Estudiantes", busca un estudiante
2. Haz clic en el botón "Editar"
3. Modifica los campos que quieras
4. Haz clic en "Guardar"
5. ✅ Cambios guardados

### Contratar un Estudiante
1. En "Estudiantes", encuentra un estudiante "Disponible"
2. Haz clic en el botón "Contratar"
3. ✅ El estado cambia a "Contratado"

---

## 📊 Estructura de Datos

```
Facultad (Ej: Ingeniería)
    ↓
Carrera (Ej: Ingeniería de Sistemas)
    ↓
Estudiante (Ej: Juan Pérez)
```

**Importante**: 
- Primero crea la Facultad
- Luego crea la Carrera dentro de esa Facultad
- Finalmente registra Estudiantes en esa Carrera

---

## 🎛️ Opciones de Género (Inclusivas)

- Masculino
- Femenino
- No Binario
- Hombre Transgénero
- Mujer Transgénero
- Genderqueer
- Asexual
- Otro
- Prefiero no decir

---

## ♿ Opciones de Discapacidad

- No (opción por defecto)
- Discapacidad Auditiva
- Discapacidad Visual
- Discapacidad Motriz
- Discapacidad Cognitiva
- Discapacidad del Habla
- Otra (especificar en un campo de texto)

---

## 🔐 Reglas de Validación

✅ El documento de identidad es único
✅ El email es único
✅ No puedes dejar campos requeridos en blanco
✅ La carrera debe pertenecer a la facultad seleccionada

---

## 🆘 Si Algo No Funciona

### El servidor no inicia
```bash
# Verifica que PostgreSQL está corriendo
sudo systemctl status postgresql

# O instala las dependencias
pip install -r requirements.txt
```

### No veo datos en el dashboard
- Espera unos segundos a que se carguen
- Recarga la página (F5 o Ctrl+R)

### Error al guardar un estudiante
- Verifica que el documento no exista ya
- Verifica que el email sea válido y único
- Revisa que completaste todos los campos requeridos

---

## 📚 Recursos Adicionales

Para más detalles, consulta:
- `GUIA_DASHBOARD_COMPLETA.md` - Guía completa
- `API_DOCUMENTATION.md` - Documentación técnica
- `INSTALL.md` - Instrucciones de instalación
- `README.md` - Resumen del proyecto

---

## ⏱️ Tiempo Total: ~5 minutos

1. Iniciar servidor ✓ (30 seg)
2. Abrir dashboard ✓ (10 seg)
3. Crear facultad ✓ (2 min)
4. Crear carrera ✓ (1.5 min)
5. Registrar estudiante ✓ (1.5 min)

**¡Ya estás listo para usar el sistema!** 🎉

---

**Versión**: 1.0.0
**Última actualización**: Marzo 13, 2026
**Estado**: ✅ Producción Lista
