# 🚀 Resumen: Configuración del Load Balancer para Practicas ITM

## Estado Actual

✅ **Docker**: La aplicación está correctamente dockerizada y configurada
✅ **Puerto 5000**: El contenedor expone correctamente el puerto 5000
✅ **Health Check**: Implementado en `/api/health`
✅ **Terraform**: Configuración de ECS y ALB lista (en tu otro repositorio)

❌ **Error Actual**: Task Definition de ECS no tiene `portMappings` definido

## El Problema en 30 Segundos

Cuando intenta crear el ECS Service con Load Balancer, AWS no sabe en qué puerto el contenedor está escuchando porque **no está definido en los `portMappings`** de la Task Definition.

## La Solución en 30 Segundos

En tu **repositorio de infraestructura**, necesitas asegurar que la `aws_ecs_task_definition` tenga:

```hcl
container_definitions = jsonencode([
  {
    name      = "practicas-itm"
    image     = var.container_image
    
    # ✅ ESTO FALTA O ESTÁ INCORRECTO
    portMappings = [
      {
        containerPort = 5000
        hostPort      = 5000
        protocol      = "tcp"
      }
    ]
  }
])
```

## Pasos Exactos

### Paso 1: Abre tu repositorio de infraestructura

```bash
cd /path/to/infrastructure/repo
cat terraform/ecs.tf | grep -A 20 "container_definitions"
```

### Paso 2: Verifica que existe `portMappings`

Si **NO LO VES**, debes agregarlo.

Si **SÍ LO VES**, verifica que sea exactamente:
```
containerPort = 5000
hostPort = 5000
protocol = "tcp"
```

### Paso 3: Valida la configuración

```bash
cd terraform/
terraform fmt -recursive
terraform validate
terraform plan
```

### Paso 4: Aplica los cambios

```bash
terraform apply
```

## Checklist de Validación

- [ ] ¿La Task Definition tiene `portMappings`?
- [ ] ¿Es `containerPort = 5000`?
- [ ] ¿Es `hostPort = 5000`?
- [ ] ¿El ECS Service tiene `container_port = 5000` en load_balancer?
- [ ] ¿El ALB Target Group tiene `port = 5000`?
- [ ] ¿El nombre del contenedor es `practicas-itm` en ambos lugares?

## Lo Que Ya Está Bien

✅ **El Dockerfile**:
- Usa Gunicorn (production-ready)
- Escucha en `0.0.0.0:5000`
- Expone el puerto 5000

✅ **El docker-compose.yml**:
- Puerto 5000 mapeado correctamente
- Health check configurado
- Variables de entorno correctas

✅ **La aplicación Flask**:
- Health check en `/api/health` funciona
- Configurada para producción
- Base de datos conectada

## Archivos de Referencia en Este Repositorio

- `docker-compose.yml` - Configuración correcta del puerto 5000
- `Dockerfile` - Configuración de Gunicorn con `--bind 0.0.0.0:5000`
- `LOADBALANCER_CONFIG.md` - Guía completa de configuración del LB
- `AWS_LOADBALANCER_SETUP.md` - Pasos específicos para AWS
- `terraform/ecs.tf` - Ejemplo de configuración correcta en este repo
- `terraform/alb.tf` - Configuración del ALB

## Comandos Útiles para Debugging

```bash
# Ver la definición actual de la tarea
aws ecs describe-task-definition \
  --task-definition practicas-itm \
  --query 'taskDefinition.containerDefinitions[0]' | jq '.'

# Ver los errores del servicio
aws ecs describe-services \
  --cluster practicas-itm-cluster \
  --services practicas-itm \
  --query 'services[0].events' | jq '.[-5:]'

# Ver logs
aws logs tail /ecs/practicas-itm --follow
```

## Si Todo Falla, Haz Esto

1. **Elimina el servicio actual** (sin eliminar el cluster):
   ```bash
   aws ecs delete-service \
     --cluster practicas-itm-cluster \
     --service practicas-itm \
     --force
   ```

2. **Corrige la Task Definition** en tu Terraform

3. **Vuelve a aplicar**:
   ```bash
   terraform apply
   ```

## Flujo Completo de Actualización

```bash
# 1. Desde tu repo de infraestructura
cd /path/to/infrastructure

# 2. Actualiza el código (agrega portMappings si no existe)
nano terraform/ecs.tf

# 3. Valida
terraform validate

# 4. Planifica
terraform plan -out=tfplan

# 5. Revisa el plan
cat tfplan  # O simplemente revisa la salida de terraform plan

# 6. Aplica
terraform apply tfplan
```

## ¿Qué Sucede Cuando Se Corrija?

1. Terraform creará una **nueva versión** de la Task Definition
2. El ECS Service se actualizará para usar la nueva versión
3. AWS desplegará nuevas tareas con la configuración correcta
4. El ALB detectará las nuevas tareas en el target group
5. El health check comenzará a pasar
6. El tráfico llegará a tu aplicación a través del load balancer

## Variables de Entorno Necesarias

El contenedor necesita estas variables (ya en docker-compose.yml):

```
DB_HOST=tu-rds-endpoint
DB_PORT=5432
DB_NAME=practicas_itm
DB_USER=practicas_user
DB_PASSWORD=***
FLASK_ENV=production
FLASK_DEBUG=False
APP_HOST=0.0.0.0
APP_PORT=5000
```

## Soporte

Si necesitas ayuda:

1. Revisa `TROUBLESHOOTING_ECS.md` en este repositorio
2. Ejecuta el script de validación: `./validate_terraform_lb.sh` desde tu repo de infra
3. Revisa los logs: `aws logs tail /ecs/practicas-itm --follow`
4. Consulta la documentación de AWS ECS

## Resumen Final

**El problema**: Tu Terraform no define `portMappings` en la Task Definition

**La solución**: Agregar 5 líneas de Terraform

**El resultado**: Tu aplicación será accesible a través del Load Balancer en el puerto 80 (ALB) que redirige a 5000 (contenedor)

---

**Próximo paso**: Abre tu repositorio de infraestructura y busca `portMappings` en `terraform/ecs.tf`. Si no lo encuentras, agrégalo y aplica los cambios.
