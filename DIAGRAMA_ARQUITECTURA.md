# 📊 DIAGRAMA DE ARQUITECTURA Y FLUJO

## 🏗️ ARQUITECTURA ACTUAL

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          INTERNET (Usuarios)                             │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
                                   │ HTTP/HTTPS
                                   │ (80/443)
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      AWS APPLICATION LOAD BALANCER                       │
│                         (practicas-itm-alb)                              │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Listener: 80 → HTTP (o 443 → HTTPS)                           │   │
│  │  Target Group: practicas-itm-tg (puerto 5000)                  │   │
│  │  Health Check: /api/health (30s interval, 5s timeout)          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
        ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
        │   ECS Task 1 │  │   ECS Task 2 │  │   ECS Task 3 │
        │ (practicas-  │  │ (practicas-  │  │ (practicas-  │
        │  itm:5000)   │  │  itm:5000)   │  │  itm:5000)   │
        └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
               │                 │                 │
               │ Docker Network (awsvpc)          │
               │                 │                 │
        ┌──────▼─────────────────▼─────────────────▼──────┐
        │         RDS PostgreSQL Database                  │
        │    (practicas-itm-db.rds.amazonaws.com)          │
        │         (Puerto 5432)                            │
        └───────────────────────────────────────────────────┘
```

## 📦 FLUJO DE LA SOLICITUD

```
1. Cliente Browser
   │
   └─→ GET http://load-balancer-dns.amazonaws.com
       │
       ▼
2. AWS ALB (Port 80)
   │ ✅ Security Group: Aceptar 80/443
   │
   └─→ Forward to Target Group (Port 5000)
       │
       ▼
3. ECS Task (Port 5000)
   │ ✅ Security Group: Aceptar 5000 desde ALB SG
   │ ✅ portMappings: containerPort=5000, hostPort=5000
   │
   └─→ Docker Container
       │ ✅ Gunicorn: --bind 0.0.0.0:5000
       │
       ▼
4. Flask Application
   │ ✅ 0.0.0.0:5000 (escucha en todas las interfaces)
   │
   ├─→ GET / (dashboard)
   ├─→ GET /api/health (health check)
   ├─→ GET /api/estudiantes
   ├─→ GET /api/facultades
   ├─→ GET /api/carreras
   └─→ GET /api/programas
       │
       ▼
5. PostgreSQL Database
   │ ✅ DB_HOST: practicas-itm-db.rds.amazonaws.com
   │ ✅ Credenciales: De Secrets Manager
   │
   └─→ Retorna datos
       │
       ▼
6. Respuesta JSON → ALB → Cliente Browser ✅
```

## 🔄 CICLO DE HEALTHCHECK

```
ALB Health Check (cada 30 segundos)
│
├─→ GET http://ECS-Task-IP:5000/api/health
│
└─→ Flask /api/health endpoint
    │
    ├─→ test_connection() a PostgreSQL
    │
    └─→ Retorna:
        {
          "status": "healthy",
          "database": "connected"
        }
        HTTP 200 ✅
        │
        ├─→ Healthy Threshold: 2 (necesita 2 checks exitosos)
        └─→ Target entra a "Healthy" y recibe tráfico
            
Si falla:
        {
          "status": "unhealthy",
          "database": "disconnected"
        }
        HTTP 503 ❌
        │
        └─→ Unhealthy Threshold: 2 (2 fallos consecutivos)
            └─→ Target entra a "Unhealthy" y se detiene tráfico
```

## 🎯 PUERTOS Y MAPEOS

```
┌──────────┬──────────────┬────────────────────────────────────────┐
│ Capa     │ Puerto       │ Descripción                            │
├──────────┼──────────────┼────────────────────────────────────────┤
│ Internet │ 80 / 443     │ ALB puertos públicos                   │
├──────────┼──────────────┼────────────────────────────────────────┤
│ ALB      │ 5000         │ Target Group backend port              │
├──────────┼──────────────┼────────────────────────────────────────┤
│ ECS Task │ 5000         │ containerPort en portMappings          │
├──────────┼──────────────┼────────────────────────────────────────┤
│ Container│ 5000         │ Gunicorn --bind 0.0.0.0:5000          │
├──────────┼──────────────┼────────────────────────────────────────┤
│ Flask    │ 5000         │ app.run(0.0.0.0:5000)                 │
├──────────┼──────────────┼────────────────────────────────────────┤
│ RDS      │ 5432         │ PostgreSQL puerto estándar             │
└──────────┴──────────────┴────────────────────────────────────────┘

FLUJO: Internet:80 → ALB:5000 → ECS:5000 → Container:5000 → Flask:5000
                                                   ↓
                                           RDS:5432
```

## 🔐 SECURITY GROUPS

```
Internet-facing
    │
    ▼
┌──────────────────────────┐
│ ALB Security Group       │
├──────────────────────────┤
│ Inbound:                 │
│  ✅ 0.0.0.0/0:80        │ (HTTP desde cualquier lugar)
│  ✅ 0.0.0.0/0:443       │ (HTTPS desde cualquier lugar)
│                          │
│ Outbound:                │
│  ✅ All traffic          │ (Necesario para alcanzar ECS SG)
└──────────────────────────┘
    │
    ▼ (al puerto 5000)
┌──────────────────────────┐
│ ECS Task Security Group  │
├──────────────────────────┤
│ Inbound:                 │
│  ✅ ALB-SG:5000         │ (Del ALB al puerto 5000)
│                          │
│ Outbound:                │
│  ✅ 0.0.0.0/0:5432      │ (A RDS puerto 5432)
│  ✅ 0.0.0.0/0:443       │ (HTTPS para actualizaciones)
└──────────────────────────┘
    │
    ▼
┌──────────────────────────┐
│ RDS Security Group       │
├──────────────────────────┤
│ Inbound:                 │
│  ✅ ECS-SG:5432         │ (Del ECS al puerto 5432)
│                          │
│ Outbound:                │
│  ✅ (normalmente no req) │
└──────────────────────────┘
```

## 📋 CHECKLIST: PUNTOS DE VERIFICACIÓN

```
┌─────────────────────────────────────────────────────────────┐
│ CONTENEDOR (Docker)                                         │
├─────────────────────────────────────────────────────────────┤
│ ✅ Dockerfile                                              │
│   └─ EXPOSE 5000                                           │
│   └─ CMD ["gunicorn", "--bind", "0.0.0.0:5000", ...]      │
│                                                             │
│ ✅ docker-compose.yml                                      │
│   └─ ports: ["5000:5000"]                                  │
│   └─ healthcheck: curl http://localhost:5000/api/health    │
│                                                             │
│ ✅ Aplicación Flask                                        │
│   └─ app.run(host="0.0.0.0", port=5000)                   │
│   └─ Endpoint: GET /api/health                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ TERRAFORM - ECS (EN TU REPO)                                │
├─────────────────────────────────────────────────────────────┤
│ ⚠️  Task Definition                                         │
│   ├─ ❌ portMappings missing o incorrecto                   │
│   │   └─ NECESITA: containerPort=5000, hostPort=5000       │
│   ├─ ✅ environment: DB_HOST, DB_PORT, etc.               │
│   └─ ✅ healthCheck: curl http://localhost:5000/api/health │
│                                                             │
│ ✅ ECS Service                                             │
│   ├─ load_balancer.container_name = "practicas-itm"       │
│   ├─ load_balancer.container_port = 5000                  │
│   └─ target_group_arn = aws_lb_target_group.app.arn       │
│                                                             │
│ ✅ ALB Target Group                                        │
│   ├─ port = 5000                                           │
│   ├─ health_check.path = "/api/health"                     │
│   ├─ health_check.port = "5000"                            │
│   └─ health_check.interval = 30                            │
│                                                             │
│ ✅ Security Groups                                         │
│   ├─ ALB SG: Inbound 0.0.0.0/0:80,443                      │
│   ├─ ECS SG: Inbound ALB-SG:5000                           │
│   └─ RDS SG: Inbound ECS-SG:5432                           │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 FLUJO DE DEPLOYMENT

```
1. Git Push
   │
   ▼
2. ECR Build
   ├─ Build image con tag:latest
   └─ Push a ECR
       │
       ▼
3. Terraform Apply
   ├─ Crear/actualizar Task Definition
   ├─ Actualizar ECS Service
   │   │
   │   └─ Rolling Update:
   │       ├─ Spin up nuevo task con nueva imagen
   │       ├─ Health check pasa
   │       ├─ ALB redirige tráfico al nuevo task
   │       └─ Terminar tarea anterior
   │
   ▼
4. Production Ready
   ├─ ECS Service: healthy
   ├─ ALB Targets: healthy (2/2 passing health checks)
   ├─ Tráfico: flowing
   └─ Aplicación: accessible via load balancer ✅
```

## 📊 ESTADOS POSIBLES DEL TARGET

```
┌──────────────────────────────────────────────────────────┐
│ Health Check Results en ALB Target Group                 │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ HEALTHY ✅                                              │
│ └─ 2+ health checks exitosos (HTTP 200)                 │
│ └─ Recibe tráfico del ALB                               │
│                                                          │
│ UNHEALTHY ❌                                            │
│ └─ 2+ health checks fallidos (timeout o error HTTP)     │
│ └─ NO recibe tráfico                                    │
│ └─ Causas:                                              │
│    ├─ Aplicación no está respondiendo                   │
│    ├─ Base de datos no conecta                          │
│    ├─ Security Group bloquea el puerto                  │
│    └─ Health check endpoint retorna error               │
│                                                          │
│ INITIAL ⏳                                              │
│ └─ Target acaba de registrarse                          │
│ └─ Esperando primer health check exitoso                │
│                                                          │
│ DRAINING 🔄                                             │
│ └─ Target siendo removido                               │
│ └─ Conexiones existentes se completan                   │
│ └─ Nuevas conexiones rechazadas                         │
└──────────────────────────────────────────────────────────┘
```

## 🧭 NAVEGACIÓN POR DOCUMENTOS

```
┌─────────────────────────────────────────────────────────┐
│ COMIENZA AQUÍ: RESUMEN_LB_CORRECCION.md                │
│ (5 minutos para entender el problema)                   │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ COPIA CÓDIGO: TERRAFORM_CODIGO_EXACTO.md               │
│ (Código listo para pegar en tu Terraform)              │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ PROFUNDIZA: LOADBALANCER_CONFIG.md                     │
│ (Detalles técnicos y configuración)                     │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ AWS ESPECÍFICO: AWS_LOADBALANCER_SETUP.md              │
│ (Pasos paso a paso para AWS)                            │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ TROUBLESHOOTING: TROUBLESHOOTING_ECS.md                │
│ (Si algo falla)                                         │
└─────────────────────────────────────────────────────────┘
```

## 📈 ESCALABILIDAD

```
Con Auto Scaling habilitado:

Load: 50% CPU
    │
    └─→ Running: 1-2 tasks (min capacity)
    
Load: 70% CPU
    │
    └─→ Policy triggered
    └─→ Spin up new task
    └─→ Running: 3 tasks
    
Load: 90% CPU
    │
    └─→ Policy triggered
    └─→ Spin up new task
    └─→ Running: 4 tasks (max capacity)
    
Load decreases
    │
    └─→ Tasks scale down después de algunos minutos
    └─→ Vuelve a: 2-3 tasks
```

---

**Conclusión**: Tu sistema está correctamente arquitecturado.
Solo necesitas agregar `portMappings` en tu Terraform y estarás listo para producción.
