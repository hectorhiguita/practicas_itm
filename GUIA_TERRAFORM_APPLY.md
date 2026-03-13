# 🚀 GUÍA FINAL: EJECUTAR TERRAFORM APPLY

## Valores Configurados

He actualizado `terraform.tfvars` con los siguientes valores:

```
✅ AWS Region:              us-east-1
✅ App Name:                practicas-itm
✅ Container Port:          5000
✅ Container CPU:           256
✅ Container Memory:        512
✅ Container Image:         450328359598.dkr.ecr.us-east-1.amazonaws.com/practicas-itm:latest
✅ Desired Count:           2
✅ DB Host:                 practicas-itm-db.c2biieuu4rfh.us-east-1.rds.amazonaws.com
✅ DB Port:                 5432
✅ DB Name:                 practicas_itm
✅ DB User:                 practicas_user
✅ DB Password:             [CONFIGURADO]
```

## 🔴 VALORES QUE NECESITAS ACTUALIZAR

En `terraform/terraform.tfvars`, actualiza estos valores con tus IDs reales de AWS:

```hcl
vpc_id = "vpc-0xxxxxxxxx"  # ← REEMPLAZA CON TU VPC ID

private_subnets = [
  "subnet-0xxxxxxxxx",     # ← REEMPLAZA
  "subnet-0yyyyyyyyy"      # ← REEMPLAZA
]

public_subnets = [
  "subnet-0zzzzzzzzz",     # ← REEMPLAZA
  "subnet-0wwwwwwwww"      # ← REEMPLAZA
]
```

### Cómo obtener estos valores:

**VPC ID:**
```bash
aws ec2 describe-vpcs \
  --filters "Name=tag:Name,Values=*" \
  --query 'Vpcs[0].VpcId' \
  --output text
```

**Subnets:**
```bash
# Privadas
aws ec2 describe-subnets \
  --filters "Name=vpc-id,Values=VPC_ID_AQUI" \
  --query 'Subnets[*].[SubnetId,AvailabilityZone,Tags[?Key==`Name`].Value|[0]]' \
  --output table

# Públicas
aws ec2 describe-subnets \
  --filters "Name=vpc-id,Values=VPC_ID_AQUI" \
  --query 'Subnets[*].[SubnetId,AvailabilityZone,Tags[?Key==`Name`].Value|[0]]' \
  --output table
```

## ⚙️ PASOS PARA EJECUTAR

### 1. Navega al directorio de Terraform

```bash
cd /home/hahiguit/Documents/POC/practicas_itm/terraform
```

### 2. Actualiza los valores de VPC y Subnets

```bash
nano terraform.tfvars

# O si prefieres script:
# Reemplaza en el archivo:
# - vpc_id
# - private_subnets
# - public_subnets
```

### 3. Verifica la configuración de Terraform

```bash
terraform fmt
terraform validate
```

**Esperado:** Sin errores

### 4. Planifica los cambios

```bash
terraform plan -out=tfplan
```

**Esto mostrará:**
- Creación del ECS Cluster
- Creación de Task Definition (CON portMappings)
- Creación del ECS Service
- Creación del ALB
- Creación de Security Groups
- Creación de Target Group
- Autoscaling

### 5. Revisa el plan (IMPORTANTE)

```bash
terraform show tfplan
```

Verifica que incluye:
- ✅ `portMappings` con `containerPort = 5000`
- ✅ `load_balancer` con `container_port = 5000`
- ✅ Target Group con `port = 5000`

### 6. Aplica los cambios

```bash
terraform apply tfplan
```

O aplicar directamente (más riesgoso):

```bash
terraform apply -auto-approve
```

### 7. Espera a que termine

Tiempo estimado: 5-10 minutos

Verás mensajes como:
```
aws_ecs_cluster.main: Creating...
aws_ecs_task_definition.app: Creating...
aws_lb.app: Creating...
...
Apply complete! Resources added: 15
```

## 📊 VERIFICAR QUE FUNCIONÓ

### 1. Ver outputs de Terraform

```bash
terraform output
```

Verás algo como:
```
alb_dns_name = "practicas-itm-alb-1234567890.us-east-1.elb.amazonaws.com"
ecs_cluster_name = "practicas-itm-cluster"
ecs_service_name = "practicas-itm-service"
```

### 2. Verificar que el ALB apunta al puerto 5000

```bash
aws elbv2 describe-target-groups \
  --names practicas-itm-tg \
  --query 'TargetGroups[0].[Port,Protocol,HealthCheckPort]'
```

Esperado:
```
[5000, HTTP, 5000]
```

### 3. Verificar que la Task Definition tiene portMappings

```bash
aws ecs describe-task-definition \
  --task-definition practicas-itm \
  --query 'taskDefinition.containerDefinitions[0].portMappings'
```

Esperado:
```
[
  {
    "containerPort": 5000,
    "hostPort": 5000,
    "protocol": "tcp"
  }
]
```

### 4. Verificar que el servicio está corriendo

```bash
CLUSTER="practicas-itm-cluster"
SERVICE="practicas-itm-service"

aws ecs describe-services \
  --cluster $CLUSTER \
  --services $SERVICE \
  --query 'services[0].[Status,RunningCount,DesiredCount]'
```

Esperado (después de 1-2 minutos):
```
[
  "ACTIVE",
  2,
  2
]
```

### 5. Verificar health check del ALB

```bash
ALB_ARN="arn:aws:elasticloadbalancing:us-east-1:450328359598:targetgroup/practicas-itm-tg/..."

aws elbv2 describe-target-health \
  --target-group-arn $ALB_ARN
```

Esperado (después de 1-2 minutos):
```
[
  {
    "TargetId": "...",
    "TargetHealth": {
      "State": "healthy",
      "Reason": "N/A",
      "Description": "N/A"
    }
  }
]
```

### 6. Acceder a la aplicación

```bash
# Obtener DNS del ALB
ALB_DNS=$(terraform output -raw alb_dns_name)

# Probar health check
curl http://$ALB_DNS/api/health

# Esperado:
# {"status": "healthy", "database": "connected"}
```

## 🆘 SI ALGO FALLA

### Error: "container port 5000 not defined"

**Ya deberías tener esto arreglado**, pero verifica:

1. En `terraform/ecs.tf`, línea ~90, existe `portMappings`
2. Contiene `containerPort = 5000`

### Error: "No suitable subnets found"

**Causa:** Los IDs de subnets son incorrectos

**Solución:**
```bash
# Obtén los IDs correctos
aws ec2 describe-subnets \
  --filters "Name=vpc-id,Values=VPC_ID" \
  --query 'Subnets[*].[SubnetId,Tags[?Key==`Name`].Value|[0]]' \
  --output table

# Actualiza terraform.tfvars con los correctos
```

### Error: "credentials not configured"

**Solución:**
```bash
aws configure
# O
export AWS_PROFILE=nombre_profile
```

### ECS Tasks no inician (Unhealthy)

Ver logs:
```bash
aws logs tail /ecs/practicas-itm --follow
```

Causas comunes:
- Imagen de Docker no existe en ECR
- Base de datos no es accesible
- Variables de entorno incorrectas

### ALB targets unhealthy

Verificar health check:
```bash
curl -v http://localhost:5000/api/health
# O desde EC2 donde corre el contenedor
```

## 📝 RESUMEN DE LO QUE SUCEDE

```
1. terraform apply
   ├─ Crea ECS Cluster
   ├─ Crea Task Definition (CON portMappings)
   ├─ Crea ECS Service
   ├─ Crea ALB (Puerto 80)
   ├─ Crea Target Group (Puerto 5000)
   └─ Crea Security Groups
   
2. ECS Service inicia Tasks
   ├─ Descarga imagen de ECR
   ├─ Inicia contenedor en puerto 5000
   └─ Registra en Target Group
   
3. ALB Health Check
   ├─ Envía GET /api/health al puerto 5000
   ├─ Espera respuesta HTTP 200
   └─ Si OK → Target "Healthy" y recibe tráfico
   
4. Tráfico hacia la aplicación
   ├─ Cliente: http://ALB_DNS/api/estudiantes
   ├─ ALB: Recibe en puerto 80, forwarda a puerto 5000
   ├─ Container: Procesa en Gunicorn
   ├─ Flask: Procesa request
   ├─ DB: Consulta a RDS
   └─ Respuesta de vuelta al cliente ✅
```

## ✅ CHECKLIST PRE-APPLY

- [ ] He reemplazado vpc_id con mi VPC real
- [ ] He reemplazado private_subnets con mis subnets reales
- [ ] He reemplazado public_subnets con mis subnets reales
- [ ] He ejecutado `terraform validate` sin errores
- [ ] He revisado `terraform plan` y veo portMappings en Task Definition
- [ ] Mi imagen está en ECR: `aws ecr describe-repositories --names practicas-itm`
- [ ] Mi base de datos está accesible desde EC2

## 🎯 COMANDOS RÁPIDOS

```bash
# Validar
cd terraform && terraform validate

# Planificar
terraform plan -out=tfplan

# Aplicar
terraform apply tfplan

# Ver outputs
terraform output

# Ver estado
terraform show

# Destruir (si algo falla)
terraform destroy -auto-approve
```

## ⏱️ TIEMPO ESTIMADO

- Obtener IDs de AWS: 5 minutos
- Actualizar terraform.tfvars: 2 minutos
- terraform validate: 1 minuto
- terraform plan: 1 minuto
- terraform apply: 10 minutos
- Verificación: 5 minutos

**TOTAL: 24 minutos**

---

**Una vez completado, tu aplicación estará accesible en:**

```
http://practicas-itm-alb-xxxx.us-east-1.elb.amazonaws.com
```

¡Éxito! 🎉
