# Solución: Puerto 5000 no definido en ECS

## Problema

```
Error: updating ECS Service (arn:aws:ecs:us-east-1:450328359598:service/practicas-itm/practicas-itm): 
operation error ECS: UpdateService, https response error StatusCode: 400, RequestID: 9aef4dc0-2dc4-408d-bcf6-a7336fbf8d1b, 
InvalidParameterException: The container practicas-itm did not have a container port 5000 defined.
```

## Causa

Cuando intentas actualizar un ECS Service con un Load Balancer, **el contenedor en la Task Definition debe tener explícitamente el puerto 5000 definido** en los `portMappings`.

Sin esto, AWS no sabe cómo routear el tráfico del ALB al contenedor.

## Solución

### 1. En la Task Definition (`ecs.tf`)

El `container_definitions` debe incluir `portMappings`:

```hcl
container_definitions = jsonencode([
  {
    name      = var.app_name
    image     = var.container_image
    essential = true
    
    # ✅ CRÍTICO: Definir los ports
    portMappings = [
      {
        containerPort = var.container_port  # 5000
        hostPort      = var.container_port  # 5000
        protocol      = "tcp"
      }
    ]
    
    # ... resto de configuración ...
  }
])
```

### 2. En el Service (`ecs.tf`)

La configuración de load_balancer debe especificar el puerto:

```hcl
resource "aws_ecs_service" "app" {
  # ... configuración ...
  
  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = var.app_name          # "practicas-itm"
    container_port   = var.container_port    # 5000 ✅
  }
}
```

### 3. En el Target Group (`alb.tf`)

El Target Group debe estar en el mismo puerto:

```hcl
resource "aws_lb_target_group" "app" {
  name        = "${var.app_name}-tg"
  port        = var.container_port  # 5000 ✅
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"
  
  health_check {
    # ... health check configuration ...
    path    = "/api/health"
    port    = tostring(var.container_port)  # "5000" ✅
  }
}
```

## Pasos para Reparar

### Opción A: Usando los archivos de Terraform proporcionados

1. **Actualizar los archivos:**
   ```bash
   cd /home/hahiguit/Documents/POC/practicas_itm/terraform
   
   # Los archivos ya contienen la configuración correcta:
   # - ecs.tf con portMappings definido
   # - alb.tf con Target Group en puerto 5000
   ```

2. **Obtener valores de AWS:**
   ```bash
   ./get_aws_values.sh
   # Esto genera terraform.tfvars con tus valores
   ```

3. **Validar y aplicar:**
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

### Opción B: Reparar manualmente en Terraform

Si ya tienes archivos de Terraform, asegúrate de que:

1. **Task Definition tenga portMappings:**
   ```hcl
   portMappings = [
     {
       containerPort = 5000
       hostPort      = 5000
       protocol      = "tcp"
     }
   ]
   ```

2. **Service tenga container_port:**
   ```hcl
   load_balancer {
     target_group_arn = aws_lb_target_group.app.arn
     container_name   = "practicas-itm"
     container_port   = 5000
   }
   ```

3. **Target Group esté en puerto 5000:**
   ```hcl
   resource "aws_lb_target_group" "app" {
     port = 5000
     # ...
   }
   ```

### Opción C: Reparar en AWS Console

1. Ir a **ECS → Task Definitions → practicas-itm**
2. Crear nueva revisión
3. Editar container definition
4. Agregar **Port Mappings**:
   - Container Port: 5000
   - Protocol: tcp
5. Guardar
6. Actualizar Service para usar la nueva task definition
7. En la configuración de Load Balancer, seleccionar:
   - Container: practicas-itm
   - Port: 5000

## Verificación

Después de aplicar la solución:

```bash
# 1. Ver si el service está en estado "RUNNING"
aws ecs describe-services \
  --cluster practicas-itm-cluster \
  --services practicas-itm-service \
  --query 'services[0].status'

# 2. Ver logs
aws logs tail /ecs/practicas-itm --follow

# 3. Probar health check
curl http://<ALB_DNS>/api/health

# 4. Ver si las tareas están sanas
aws ecs describe-tasks \
  --cluster practicas-itm-cluster \
  --tasks $(aws ecs list-tasks --cluster practicas-itm-cluster --query 'taskArns[0]' --output text) \
  --query 'tasks[0].lastStatus'
```

## Resumen de Cambios

| Componente | Cambio |
|---|---|
| **Task Definition** | ✅ Agregar `portMappings` con puerto 5000 |
| **ECS Service** | ✅ Especificar `container_port = 5000` en load_balancer |
| **Target Group** | ✅ Configurar `port = 5000` |
| **Health Check** | ✅ Verificar que apunta a puerto 5000 |

## Archivos Proporcionados

```
terraform/
├── main.tf              # ✅ Provider configuration
├── variables.tf         # ✅ Variable definitions
├── ecs.tf              # ✅ ECS con portMappings CORRECTO
├── alb.tf              # ✅ ALB con puerto 5000
├── terraform.tfvars.example
├── get_aws_values.sh   # Script para autoconfigurar
└── README.md           # Documentación completa
```

## Próximos Pasos

1. ✅ Ejecutar `./get_aws_values.sh` para generar `terraform.tfvars`
2. ✅ Ejecutar `terraform init && terraform plan && terraform apply`
3. ✅ Verificar que el ALB está funcionando:
   ```bash
   terraform output alb_dns_name
   curl http://<ALB_DNS>/api/health
   ```
4. ✅ Ver logs en CloudWatch

¡El problema debe estar resuelto! 🎉
