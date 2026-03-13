# 📚 ÍNDICE DE DOCUMENTACIÓN - CONFIGURACIÓN DEL LOAD BALANCER

## 🔴 TU PROBLEMA ACTUAL

```
Error: updating ECS Service: InvalidParameterException: 
The container practicas-itm did not have a container port 5000 defined
```

**Solución rápida**: Ve a `RESUMEN_LB_CORRECCION.md`  
**Código para copiar-pegar**: Ve a `TERRAFORM_CODIGO_EXACTO.md`

---

## 📖 DOCUMENTACIÓN COMPLETA

### 1. 🚨 PARA RESOLVER TU ERROR INMEDIATAMENTE

| Documento | Contenido | Lectura |
|-----------|----------|---------|
| **RESUMEN_LB_CORRECCION.md** | Resumen ejecutivo del problema y solución | 5 min |
| **TERRAFORM_CODIGO_EXACTO.md** | Código Terraform listo para copiar-pegar | 10 min |

**→ EMPIEZA AQUÍ**

---

### 2. 🔧 DOCUMENTACIÓN TÉCNICA DETALLADA

| Documento | Contenido | Público | Privado |
|-----------|----------|---------|---------|
| **LOADBALANCER_CONFIG.md** | Configuración completa del LB | ✅ | - |
| **AWS_LOADBALANCER_SETUP.md** | Guía paso a paso para AWS ALB | ✅ | ✅ |
| **SOLUCION_PUERTO_5000.md** | Explicación detallada del error | ✅ | ✅ |

**→ CONSULTA ESTOS PARA DETALLES**

---

### 3. 🔍 SCRIPTS DE VERIFICACIÓN

| Script | Propósito | Uso |
|--------|-----------|-----|
| **verify_lb_config.sh** | Verifica docker-compose local | `./verify_lb_config.sh` |
| **validate_terraform_lb.sh** | Valida Terraform en repo de infra | `./validate_terraform_lb.sh` |

**→ EJECUTA ESTOS PARA VERIFICAR**

---

### 4. 🐳 CONFIGURACIÓN DOCKER

| Archivo | Estado | Descripción |
|---------|--------|-------------|
| **Dockerfile** | ✅ Listo | Gunicorn con --bind 0.0.0.0:5000 |
| **docker-compose.yml** | ✅ Actualizado | Puerto 5000 mapeado, health check |
| **docker-compose.prod.yml** | 🆕 Nuevo | Múltiples instancias para escalado |
| **nginx.conf** | 🆕 Nuevo | NGINX como LB local |

**→ ESTOS YA ESTÁN CORRECTAMENTE CONFIGURADOS**

---

## 🎯 FLUJO DE LECTURA RECOMENDADO

### Para resolver rápidamente:

1. Lee **RESUMEN_LB_CORRECCION.md** (5 min)
2. Copia código de **TERRAFORM_CODIGO_EXACTO.md**
3. Pégalo en tu `terraform/ecs.tf`
4. Ejecuta `terraform apply`
5. ¡Listo!

### Para entender profundamente:

1. Lee **SOLUCION_PUERTO_5000.md**
2. Lee **LOADBALANCER_CONFIG.md**
3. Lee **AWS_LOADBALANCER_SETUP.md**
4. Ejecuta `verify_lb_config.sh` para validar Docker
5. Ejecuta `validate_terraform_lb.sh` en tu repo de infra
6. Aplica cambios en Terraform

---

## 🔑 PUNTOS CLAVE

### ✅ LO QUE YA ESTÁ BIEN

```
Docker Container
└─ Dockerfile
   └─ Gunicorn: --bind 0.0.0.0:5000 ✅
   └─ Healthcheck: curl http://localhost:5000/api/health ✅
   
Aplicación Flask
└─ Escucha en 0.0.0.0:5000 ✅
└─ Endpoint /api/health disponible ✅
└─ Configuración de producción ✅

Docker Compose
└─ Puerto 5000 expuesto ✅
└─ Health check implementado ✅
└─ Red bridge (practicas_network) ✅
└─ Variables de entorno correctas ✅
```

### ❌ LO QUE FALTA (EN TU REPO DE INFRA)

```
Terraform Task Definition
└─ portMappings NO DEFINIDO ❌
   └─ Necesita:
      └─ containerPort: 5000
      └─ hostPort: 5000
      └─ protocol: tcp
```

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN

### Fase 1: Docker (YA COMPLETADO)
- [x] Dockerfile con Gunicorn
- [x] docker-compose.yml con puerto 5000
- [x] Health check en /api/health
- [x] Aplicación Flask correctamente configurada

### Fase 2: Terraform (EN PROGRESO)
- [ ] Agregar portMappings en Task Definition
- [ ] Verificar container_name coincide
- [ ] Verificar container_port = 5000 en Service
- [ ] Verificar port = 5000 en Target Group
- [ ] terraform validate
- [ ] terraform plan
- [ ] terraform apply

### Fase 3: Verificación Post-Deployment
- [ ] ECS Service corriendo
- [ ] Health check pasando
- [ ] ALB targets sanos
- [ ] Tráfico llegando a la aplicación

---

## 🔗 REFERENCIAS RÁPIDAS

### Comandos Docker

```bash
# Iniciar
docker-compose up -d

# Ver estado
docker-compose ps

# Logs
docker-compose logs -f api

# Health check
curl http://localhost:5000/api/health

# Ejecutar script de verificación
./verify_lb_config.sh
```

### Comandos Terraform

```bash
# Validar
terraform validate

# Planificar
terraform plan

# Aplicar
terraform apply

# Ejecutar script de validación (en repo de infra)
./validate_terraform_lb.sh
```

### Comandos AWS CLI

```bash
# Ver Task Definition
aws ecs describe-task-definition --task-definition practicas-itm \
  --query 'taskDefinition.containerDefinitions[0].portMappings'

# Ver Service
aws ecs describe-services --cluster practicas-itm-cluster \
  --services practicas-itm-service

# Ver Target Health
aws elbv2 describe-target-health --target-group-arn <ARN>

# Ver Logs
aws logs tail /ecs/practicas-itm --follow
```

---

## 🆘 TROUBLESHOOTING RÁPIDO

| Síntoma | Causa | Solución |
|---------|-------|----------|
| "container port 5000 not defined" | portMappings no existe en Task Def | Ver TERRAFORM_CODIGO_EXACTO.md |
| Health check falla | BD no conecta | Ver logs: `aws logs tail /ecs/practicas-itm` |
| ALB no alcanza contenedor | Security Group incorrecto | Ver AWS_LOADBALANCER_SETUP.md |
| Contenedor no inicia | Imagen no existe o es incorrecta | Ver `terraform.tfvars` container_image |

---

## 📞 ¿NECESITAS AYUDA?

1. **Problema rápido** → RESUMEN_LB_CORRECCION.md
2. **Error específico** → SOLUCION_PUERTO_5000.md
3. **AWS specific** → AWS_LOADBALANCER_SETUP.md
4. **Troubleshooting** → TROUBLESHOOTING_ECS.md
5. **Verificar setup** → verify_lb_config.sh + validate_terraform_lb.sh

---

## 📁 ESTRUCTURA DE ARCHIVOS

```
practicas_itm/
├── 📚 DOCUMENTACIÓN
│   ├── RESUMEN_LB_CORRECCION.md          ← EMPIEZA AQUÍ
│   ├── TERRAFORM_CODIGO_EXACTO.md        ← COPIA-PEGA
│   ├── LOADBALANCER_CONFIG.md
│   ├── AWS_LOADBALANCER_SETUP.md
│   ├── SOLUCION_PUERTO_5000.md
│   └── INDEX_LB.md                       ← AQUÍ ESTÁS
│
├── 🔧 SCRIPTS
│   ├── verify_lb_config.sh               (local)
│   └── validate_terraform_lb.sh          (remote infra)
│
├── 🐳 DOCKER
│   ├── Dockerfile                        ✅
│   ├── docker-compose.yml                ✅
│   ├── docker-compose.prod.yml           🆕
│   └── nginx.conf                        🆕
│
├── 📊 TERRAFORM (REFERENCIA)
│   ├── terraform/ecs.tf                  (ejemplo)
│   ├── terraform/alb.tf                  (ejemplo)
│   ├── terraform/variables.tf            (ejemplo)
│   └── terraform/terraform.tfvars.example (ejemplo)
│
└── 🐍 APLICACIÓN
    └── src/
        └── api/
            └── app.py                    (Flask con /api/health)
```

---

## ✨ RESUMIENDO

Tu aplicación **YA ESTÁ LISTA** para el Load Balancer.

Todo lo que necesitas hacer es:

1. Abre tu repositorio de infraestructura
2. Busca `container_definitions` en `terraform/ecs.tf`
3. Agrega `portMappings` (o corrígelo si ya existe)
4. Ejecuta `terraform apply`

**Done.** El resto ya está configurado correctamente.

---

**Última actualización**: 2024-01-13  
**Versión**: 1.0  
**Estado**: Listo para producción
