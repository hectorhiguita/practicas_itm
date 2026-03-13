# ✅ CHECKLIST FINAL - ANTES DE TERRAFORM APPLY

## 📋 VERIFICACIÓN PREVIA

### 1. ECR Repository ✅
- [x] URL ECR: `450328359598.dkr.ecr.us-east-1.amazonaws.com/practicas-itm`
- [x] Imagen disponible: `:latest`

Comando para verificar:
```bash
aws ecr describe-repositories --repository-names practicas-itm
```

### 2. Docker Configuration ✅
- [x] Dockerfile usa Gunicorn
- [x] Expone puerto 5000
- [x] Comando: `gunicorn --bind 0.0.0.0:5000`
- [x] Health endpoint: `/api/health`

### 3. terraform.tfvars ⚠️ (NECESITA ACTUALIZACIÓN)

#### Valores YA CONFIGURADOS:
```
✅ aws_region                = "us-east-1"
✅ app_name                  = "practicas-itm"
✅ container_port            = 5000              [CRÍTICO]
✅ container_cpu             = 256
✅ container_memory          = 512
✅ container_image           = "450328359598.dkr.ecr.us-east-1.amazonaws.com/practicas-itm:latest"
✅ desired_count             = 2
✅ db_host                   = "practicas-itm-db.c2biieuu4rfh.us-east-1.rds.amazonaws.com"
✅ db_port                   = 5432
✅ db_name                   = "practicas_itm"
✅ db_user                   = "practicas_user"
✅ db_password               = "0n3P13c32024*"
```

#### Valores QUE NECESITAN ACTUALIZACIÓN:
```
❌ vpc_id                    = "vpc-0xxxxxxxxx"        ← REEMPLAZA
❌ private_subnets[0]        = "subnet-0xxxxxxxxx"     ← REEMPLAZA
❌ private_subnets[1]        = "subnet-0yyyyyyyyy"     ← REEMPLAZA
❌ public_subnets[0]         = "subnet-0zzzzzzzzz"     ← REEMPLAZA
❌ public_subnets[1]         = "subnet-0wwwwwwwww"     ← REEMPLAZA
```

### 4. Terraform Files ✅
- [x] `terraform/main.tf` - Existe
- [x] `terraform/variables.tf` - Define variables necesarias
- [x] `terraform/ecs.tf` - Task Definition CON `portMappings`
- [x] `terraform/alb.tf` - ALB con Target Group en puerto 5000
- [x] `terraform/terraform.tfvars` - Creado y configurado

## 🔧 PASOS ANTES DE APLICAR

### PASO 1: Obtener tus IDs de AWS

```bash
# 1.1 VPC ID
aws ec2 describe-vpcs \
  --query 'Vpcs[0].VpcId' \
  --output text

# Copiar el valor que empieza con vpc-

# 1.2 Subnets
aws ec2 describe-subnets \
  --query 'Subnets[*].[SubnetId,Tags[?Key==`Name`].Value|[0],AvailabilityZone]' \
  --output table

# Copiar 2 subnets que digan "Private" para private_subnets
# Copiar 2 subnets que digan "Public" para public_subnets
```

### PASO 2: Actualizar terraform.tfvars

```bash
cd /home/hahiguit/Documents/POC/practicas_itm/terraform
nano terraform.tfvars

# Actualiza estos campos:
vpc_id = "vpc-xxxxxxxx"                # Tu VPC ID
private_subnets = [
  "subnet-xxxxxxxx",                    # Primera subnet privada
  "subnet-yyyyyyyy"                     # Segunda subnet privada
]
public_subnets = [
  "subnet-zzzzzzzz",                    # Primera subnet pública
  "subnet-wwwwwwww"                     # Segunda subnet pública
]
```

### PASO 3: Validar Terraform

```bash
terraform fmt -recursive

# Debe terminar sin errores
```

```bash
terraform validate

# Debe retornar: Success! The configuration is valid.
```

### PASO 4: Ver el plan

```bash
terraform plan -out=tfplan

# Revisar que incluya:
# - aws_ecs_cluster
# - aws_ecs_task_definition (CON portMappings)
# - aws_ecs_service
# - aws_lb (ALB)
# - aws_lb_target_group (puerto 5000)
# - aws_security_group
```

### PASO 5: Verificar portMappings en el plan

```bash
terraform show tfplan | grep -A 10 "portMappings"

# Debe mostrar:
# "port_mappings": [
#   {
#     "container_port": 5000,
#     "host_port": 5000,
#     "protocol": "tcp"
#   }
# ]
```

### PASO 6: Ejecutar Apply

```bash
terraform apply tfplan
```

O si confías, directamente:
```bash
terraform apply -auto-approve
```

## 📊 VERIFICACIÓN POST-APPLY

### Esperar a que termine (5-10 minutos)

Señales de éxito:
```
Apply complete! Resources added: 15
```

### Obtener outputs

```bash
terraform output

# Verás algo como:
# alb_dns_name = "practicas-itm-alb-1234.us-east-1.elb.amazonaws.com"
# ecs_cluster_name = "practicas-itm-cluster"
# ecs_service_name = "practicas-itm-service"
```

### Verificación 1: Task Definition con portMappings

```bash
aws ecs describe-task-definition \
  --task-definition practicas-itm \
  --query 'taskDefinition.containerDefinitions[0].portMappings'

# Esperado:
# [
#   {
#     "containerPort": 5000,
#     "hostPort": 5000,
#     "protocol": "tcp"
#   }
# ]
```

### Verificación 2: Target Group Puerto 5000

```bash
aws elbv2 describe-target-groups \
  --names practicas-itm-tg \
  --query 'TargetGroups[0].[Port,Protocol,HealthCheckPort]'

# Esperado:
# [5000, "HTTP", "5000"]
```

### Verificación 3: ECS Service Corriendo

```bash
CLUSTER="practicas-itm-cluster"
SERVICE="practicas-itm-service"

aws ecs describe-services \
  --cluster $CLUSTER \
  --services $SERVICE \
  --query 'services[0].[Status,RunningCount,DesiredCount]'

# Esperado (después de 2-3 minutos):
# ["ACTIVE", 2, 2]
```

### Verificación 4: Target Health

```bash
TARGET_GROUP_ARN=$(aws elbv2 describe-target-groups \
  --names practicas-itm-tg \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)

aws elbv2 describe-target-health --target-group-arn $TARGET_GROUP_ARN

# Esperado (después de 1-2 minutos):
# "State": "healthy"
```

### Verificación 5: Health Check de la Aplicación

```bash
ALB_DNS=$(terraform output -raw alb_dns_name)

curl http://$ALB_DNS/api/health

# Esperado:
# {"status": "healthy", "database": "connected"}
```

### Verificación 6: Acceso a la API

```bash
curl http://$ALB_DNS/api/estudiantes

# Debe retornar JSON con datos de estudiantes
```

## 🆘 SI ALGO FALLA

### Error: "No suitable subnets found"

**Causa:** IDs de subnets incorrectos

**Solución:**
```bash
# Obtén los IDs correctos
aws ec2 describe-subnets \
  --filters "Name=vpc-id,Values=TU_VPC_ID" \
  --query 'Subnets[*].[SubnetId,Tags[?Key==`Name`].Value|[0]]' \
  --output table

# Actualiza terraform.tfvars y vuelve a aplicar
terraform apply
```

### Error: "container port 5000 not defined"

**Causa:** portMappings no está en la Task Definition

**Verificar en ecs.tf línea ~90:**
```hcl
portMappings = [
  {
    containerPort = 5000
    hostPort      = 5000
    protocol      = "tcp"
  }
]
```

### Targets "Unhealthy"

**Causas posibles:**
1. Imagen de Docker no existe en ECR
2. Base de datos no es accesible
3. Health endpoint no responde

**Debugging:**
```bash
# Ver logs de la tarea
aws logs tail /ecs/practicas-itm --follow

# Ver eventos del servicio
aws ecs describe-services \
  --cluster practicas-itm-cluster \
  --services practicas-itm-service \
  --query 'services[0].events' | head -5
```

### Error: "ECR image not found"

**Causa:** Imagen no está en ECR o tag es incorrecto

**Solución:**
```bash
# Verificar imágenes en ECR
aws ecr describe-images \
  --repository-name practicas-itm

# Build y push de la imagen
docker build -t practicas-itm:latest .
aws ecr get-login-password | docker login --username AWS --password-stdin 450328359598.dkr.ecr.us-east-1.amazonaws.com
docker tag practicas-itm:latest 450328359598.dkr.ecr.us-east-1.amazonaws.com/practicas-itm:latest
docker push 450328359598.dkr.ecr.us-east-1.amazonaws.com/practicas-itm:latest
```

## 📝 RESUMEN

| Paso | Estado | Comando |
|------|--------|---------|
| 1. Obtener IDs AWS | ⏳ Pendiente | `aws ec2 describe-vpcs ...` |
| 2. Actualizar tfvars | ⏳ Pendiente | `nano terraform.tfvars` |
| 3. Validar | ⏳ Pendiente | `terraform validate` |
| 4. Planificar | ⏳ Pendiente | `terraform plan` |
| 5. Aplicar | ⏳ Pendiente | `terraform apply` |
| 6. Verificar | ⏳ Pendiente | `curl ALB_DNS/api/health` |

## 🎯 RESULTADO ESPERADO

Cuando todo funciona correctamente:

```
Internet (usuario)
    ↓ HTTP:80
ALB (load balancer)
    ↓ HTTP:5000
ECS Tasks (2 instancias)
    ├─ Container 1: Gunicorn en 0.0.0.0:5000
    └─ Container 2: Gunicorn en 0.0.0.0:5000
    ↓
Flask Application
    ↓
RDS PostgreSQL

Status: ✅ HEALTHY
```

---

**¡Estás listo para ejecutar `terraform apply`!** 🚀
