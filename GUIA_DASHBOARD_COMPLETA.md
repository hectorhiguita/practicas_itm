# 📚 Guía Completa del Dashboard - Practicas ITM

## 🎯 Inicio Rápido

### Acceso al Dashboard
```bash
# El dashboard está disponible en:
http://localhost:5000
```

## 📋 Secciones del Dashboard

### 1. **Dashboard** (Inicio)
Vista general con estadísticas:
- **Total Estudiantes**: Cantidad total de estudiantes registrados
- **Disponibles**: Estudiantes listos para prácticas
- **Contratados**: Estudiantes en prácticas activas
- **Finalizados**: Estudiantes que completaron sus prácticas
- **Total Carreras**: Número de programas académicos
- **Total Facultades**: Número de facultades

**Últimos Estudiantes Registrados**: Lista de los 5 últimos estudiantes agregados

---

### 2. **Gestión de Estudiantes** 👨‍🎓

#### Agregar Nuevo Estudiante

**Campos Requeridos:**
```
✓ Documento de Identidad (único)
✓ Nombre
✓ Apellido
✓ Correo Electrónico (único)
✓ Teléfono
✓ Género
✓ Facultad
✓ Programa o Carrera
```

**Campos Opcionales:**
```
○ ¿Presenta alguna discapacidad?
  - Si selecciona "Otra", aparece un campo para especificar
```

**Opciones de Género Disponibles:**
- Masculino
- Femenino
- No Binario
- Hombre Transgénero
- Mujer Transgénero
- Genderqueer
- Asexual
- Otro
- Prefiero no decir

**Opciones de Discapacidad:**
- No (por defecto)
- Discapacidad Auditiva
- Discapacidad Visual
- Discapacidad Motriz
- Discapacidad Cognitiva
- Discapacidad del Habla
- Otra (permite especificar)

#### Funcionalidades de Búsqueda y Filtrado

**Buscador**: Filtra por nombre, apellido, documento o email

**Filtro por Estado:**
- Todos los estados
- Disponible
- Contratado
- Por Finalizar
- Finalizó

**Filtro por Carrera**: Muestra solo estudiantes de una carrera específica

#### Acciones sobre Estudiantes

**Editar**: 
- Actualiza todos los datos del estudiante
- Preserva el documento de identidad (no se puede cambiar)

**Eliminar**: 
- Elimina permanentemente el estudiante y sus datos

**Contratar**: 
- Disponible solo para estudiantes con estado "Disponible"
- Cambia el estado a "Contratado"

---

### 3. **Gestión de Carreras** 📚

#### Agregar Nueva Carrera

**Campos Requeridos:**
```
✓ Nombre de la Carrera
✓ Facultad
```

**Campos Opcionales:**
```
○ Descripción
```

#### Acciones sobre Carreras

**Editar**: 
- Actualiza nombre, descripción y facultad

**Eliminar**: 
- Elimina la carrera
- ⚠️ Nota: No se puede eliminar si tiene estudiantes asociados

**Búsqueda**: 
- Filtra por nombre o descripción de carrera

---

### 4. **Gestión de Facultades** 🏫

#### Agregar Nueva Facultad

**Campos Requeridos:**
```
✓ Nombre de la Facultad
```

**Campos Opcionales:**
```
○ Descripción
```

#### Acciones sobre Facultades

**Editar**: 
- Actualiza nombre y descripción

**Eliminar**: 
- Elimina la facultad
- ⚠️ Nota: No se puede eliminar si tiene carreras o estudiantes

**Búsqueda**: 
- Filtra por nombre o descripción

---

## 🔄 Flujo de Trabajo Recomendado

### Para crear un nuevo estudiante:

1. **Crear Facultad** (si no existe)
   - Ir a "Gestión de Facultades"
   - Hacer clic en "+ Agregar"
   - Completar nombre y descripción
   - Guardar

2. **Crear Carrera** (asociada a la facultad)
   - Ir a "Gestión de Carreras"
   - Hacer clic en "+ Agregar"
   - Seleccionar la facultad
   - Completar nombre y descripción
   - Guardar

3. **Crear Estudiante** (asociado a la carrera)
   - Ir a "Gestión de Estudiantes"
   - Hacer clic en "+ Agregar"
   - Completar todos los campos requeridos
   - Seleccionar facultad
   - Seleccionar carrera (se filtra automáticamente)
   - Indicar si presenta discapacidad
   - Guardar

---

## 💡 Consejos de Uso

### Validaciones Automáticas

✅ **Documento Único**: No puede haber dos estudiantes con el mismo documento
✅ **Email Único**: No puede haber dos estudiantes con el mismo email
✅ **Carrera pertenece a Facultad**: Al guardar, se valida que la carrera seleccionada pertenezca a la facultad
✅ **Campos Requeridos**: No permite guardar sin completar campos obligatorios

### Filtrado de Carreras

Cuando agrega o edita un estudiante:
1. Selecciona una Facultad
2. Las opciones de Carrera se filtran automáticamente
3. Solo muestra carreras de esa facultad
4. Si cambia de facultad, las carreras se actualizan

### Discapacidad Personalizada

Si selecciona "Otra" en discapacidades:
1. Aparece un campo de texto
2. Aquí puede especificar la discapacidad exacta
3. Si cambia de opción, el campo desaparece
4. El texto se borra si no está seleccionada "Otra"

---

## 📊 Datos que se Capturan

### Por Estudiante:
- Documento de identidad (único)
- Nombre y apellido
- Email (único)
- Teléfono
- Género
- Facultad
- Carrera/Programa
- Discapacidad (si aplica)
- Estado de práctica
- Fecha de creación y actualización

### Por Carrera:
- Nombre
- Descripción
- Facultad asociada
- Fecha de creación

### Por Facultad:
- Nombre
- Descripción
- Fecha de creación

---

## 🔐 Seguridad

### Claves Únicas:
- ✅ Documento de identidad (por estudiante)
- ✅ Email (por estudiante)
- ✅ Nombre de facultad (única)

### Integridad Referencial:
- ✅ No puede crear carrera sin facultad
- ✅ No puede crear estudiante sin carrera
- ✅ No puede eliminar facultad si tiene carreras/estudiantes

---

## 🐛 Solución de Problemas

### "No hay estudiantes registrados"
**Solución**: Haga clic en "+ Agregar" para crear el primer estudiante

### "Carrera no aparece en la lista"
**Problema**: La carrera pertenece a otra facultad
**Solución**: Seleccione la facultad correcta

### "No puedo eliminar una facultad"
**Problema**: Tiene carreras o estudiantes asociados
**Solución**: Elimine primero los estudiantes y carreras de esa facultad

### "Error al guardar un estudiante"
**Solución**: 
- Verifique que el documento no exista ya
- Verifique que el email sea único
- Complete todos los campos requeridos

---

## 📱 Compatibilidad

✅ **Desktop**: Navegadores modernos (Chrome, Firefox, Safari, Edge)
✅ **Tablet**: Interfaz responsive
✅ **Móvil**: Diseño adaptativo (algunos campos pueden requerir scroll)

---

## 🚀 Características Destacadas

1. **Interfaz Intuitiva**: Diseño moderno y fácil de usar
2. **Búsqueda y Filtrado**: Encuentra información rápidamente
3. **Validaciones**: Previene datos inválidos o duplicados
4. **Inclusividad**: Opciones LGBTQ+ en géneros
5. **Accesibilidad**: Soporte para personas con discapacidades
6. **Estadísticas en Tiempo Real**: Dashboard actualizado automáticamente
7. **Notificaciones**: Confirmación visual de acciones (toasts)

---

## 📞 Soporte

Para reportar problemas o sugerencias, consulte con el administrador del sistema.

**Versión**: 1.0.0
**Última actualización**: Marzo 13, 2026
