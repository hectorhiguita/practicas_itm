# Troubleshooting: ECS Service con Load Balancer

## Error: "Container X did not have a container port Y defined"

### Diagnóstico

```bash
# 1. Ver la Task Definition actual
aws ecs describe-task-definition \
  --task-definition practicas-itm \
  --query 'taskDefinition.containerDefinitions[0].portMappings'

# Resultado esperado:
# [
#     {
#         "containerPort": 5000,
#         "hostPort": 5000,
#         "protocol": "tcp"
#     }
# ]

# 2. Si está vacío, es el problema
```

### Solución Rápida

```bash
# Opción A: Terraform
cd terraform
terraform apply -var="desired_count=2"

# Opción B: AWS CLI
# 1. Crear nueva Task Definition revision con portMappings
# 2. Actualizar Service con la nueva revision
```

## Error: "Target group not associated with the service"

### Solución

Asegúrate que en el Service hay una configuración de load_balancer:

```hcl
resource "aws_ecs_service" "app" {
  # ... configuración ...
  
  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = var.app_name
    container_port   = var.container_port
  }
}
```

## Health Check Falla

### Diagnóstico

```bash
# 1. Ver estado del target group
aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:...

# 2. Ver logs de la aplicación
aws logs tail /ecs/practicas-itm --follow

# 3. Conectarse al contenedor
aws ecs execute-command \
  --cluster practicas-itm-cluster \
  --task <task-id> \
  --container practicas-itm \
  --interactive \
  --command "/bin/bash"

# 4. Dentro del contenedor:
curl http://localhost:5000/api/health
```

### Problemas Comunes

| Síntoma | Causa | Solución |
|---|---|---|
| Health check timeout | Aplicación lenta | Aumentar timeout en TG |
| Health check falla | App no responde en /api/health | Verificar app está corriendo |
| Port unreachable | Puerto no expuesto | Agregar portMappings |
| Connection refused | Firewall/SG | Verificar security groups |

## Service está "RUNNING" pero tareas fallas

```bash
# Ver por qué falla
aws ecs describe-tasks \
  --cluster practicas-itm-cluster \
  --tasks <task-id> \
  --query 'tasks[0].stoppedReason'

# Ver logs
aws logs tail /ecs/practicas-itm --follow

# Causas comunes:
# - BD no accesible
# - Imagen Docker corrupta
# - Permisos insuficientes
# - Variable de entorno faltante
```

## ALB no está alcanzando la aplicación

### Verificación de Security Groups

```bash
# ALB SG debe permitir tráfico saliente al puerto 5000
aws ec2 describe-security-groups \
  --group-ids sg-alb-id \
  --query 'SecurityGroups[0].IpPermissions'

# ECS SG debe permitir tráfico entrante desde ALB SG
aws ec2 describe-security-groups \
  --group-ids sg-ecs-id \
  --query 'SecurityGroups[0].IpPermissions'
```

### Verificación de Subnets

```bash
# ALB debe estar en subnets públicas
# ECS debe estar en subnets privadas o públicas

# Ver subnets
aws ec2 describe-subnets --subnet-ids subnet-xxx
```

## Escalar el servicio

```bash
# Ver configuración actual
aws ecs describe-services \
  --cluster practicas-itm-cluster \
  --services practicas-itm-service

# Escalar manualmente
aws ecs update-service \
  --cluster practicas-itm-cluster \
  --service practicas-itm-service \
  --desired-count 4

# Con Terraform
terraform apply -var="desired_count=4"
```

## Actualizar la aplicación

```bash
# 1. Subir nueva imagen a ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 450328359598.dkr.ecr.us-east-1.amazonaws.com
docker build -t practicas-itm:v2 .
docker tag practicas-itm:v2 450328359598.dkr.ecr.us-east-1.amazonaws.com/practicas-itm:v2
docker push 450328359598.dkr.ecr.us-east-1.amazonaws.com/practicas-itm:v2

# 2. Actualizar con Terraform
terraform apply -var="container_image=450328359598.dkr.ecr.us-east-1.amazonaws.com/practicas-itm:v2"

# 3. Verificar despliegue
aws ecs describe-services \
  --cluster practicas-itm-cluster \
  --services practicas-itm-service \
  --query 'services[0].deployments'
```

## Ver Métricas de CloudWatch

```bash
# CPU utilization
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=practicas-itm-service \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 300 \
  --statistics Average

# Memory utilization
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name MemoryUtilization \
  --dimensions Name=ServiceName,Value=practicas-itm-service \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 300 \
  --statistics Average
```

## Deshacer cambios

```bash
# Ver historial
terraform show

# Rollback a revisión anterior de Task Definition
aws ecs update-service \
  --cluster practicas-itm-cluster \
  --service practicas-itm-service \
  --task-definition practicas-itm:2

# O con Terraform
terraform destroy
```

## Comandos Útiles

```bash
# Información general
aws ecs describe-clusters --clusters practicas-itm-cluster

# Ver servicios
aws ecs list-services --cluster practicas-itm-cluster

# Ver tareas
aws ecs list-tasks --cluster practicas-itm-cluster

# Ver logs
aws logs describe-log-groups | grep ecs
aws logs tail /ecs/practicas-itm --follow

# Ver ALB
aws elbv2 describe-load-balancers --names practicas-itm-alb

# Ver Target Group
aws elbv2 describe-target-groups --names practicas-itm-tg

# Ver Target Health
aws elbv2 describe-target-health --target-group-arn arn:aws:...
```

## Checklist Final

- [ ] Task Definition tiene `portMappings` definido
- [ ] Service tiene `load_balancer` configurado
- [ ] Target Group está en puerto 5000
- [ ] Health check path es `/api/health`
- [ ] Security groups permiten tráfico
- [ ] Subnets están correctas
- [ ] Imagen Docker está en ECR
- [ ] Variables de entorno están seteadas
- [ ] RDS es accesible desde ECS
- [ ] ALB DNS funciona con curl

## Soporte Adicional

Si los problemas persisten:

1. Revertir a una configuración conocida funcionando
2. Revisar logs en CloudWatch
3. Verificar tareas individuales
4. Contactar a soporte de AWS si es necesario

```bash
# Colectar todos los datos para debugging
./collect_debug_info.sh
```
