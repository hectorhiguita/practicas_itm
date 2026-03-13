# 📋 Código Terraform Exacto para Corregir el Error

Este documento contiene el código **exacto** que necesitas en tu repositorio de infraestructura.

## Error que Recibiste

```
InvalidParameterException: The container practicas-itm did not have a container port 5000 defined.
```

## Solución: Código Completo

Copia y pega este código en tu archivo `terraform/ecs.tf` (reemplazando la sección correspondiente):

### 1. Task Definition Completa

```hcl
# ECS Task Definition - Con puerto 5000 correctamente definido
resource "aws_ecs_task_definition" "app" {
  family                   = var.app_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.container_cpu                    # ej: 256
  memory                   = var.container_memory                 # ej: 512
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = var.app_name  # ej: "practicas-itm"
      image     = var.container_image
      essential = true

      # ✅ CRÍTICO: Definición del puerto 5000
      portMappings = [
        {
          containerPort = 5000
          hostPort      = 5000
          protocol      = "tcp"
        }
      ]

      # Variables de entorno públicas
      environment = [
        {
          name  = "DB_HOST"
          value = var.db_host
        },
        {
          name  = "DB_PORT"
          value = tostring(var.db_port)
        },
        {
          name  = "DB_NAME"
          value = var.db_name
        },
        {
          name  = "DB_USER"
          value = var.db_user
        },
        {
          name  = "FLASK_ENV"
          value = "production"
        },
        {
          name  = "FLASK_DEBUG"
          value = "False"
        },
        {
          name  = "APP_HOST"
          value = "0.0.0.0"
        },
        {
          name  = "APP_PORT"
          value = "5000"
        }
      ]

      # Secretos desde Secrets Manager (DB_PASSWORD, SECRET_KEY)
      secrets = [
        {
          name      = "DB_PASSWORD"
          valueFrom = aws_secretsmanager_secret.db_password.arn
        },
        {
          name      = "SECRET_KEY"
          valueFrom = aws_secretsmanager_secret.flask_secret_key.arn
        }
      ]

      # CloudWatch Logs
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs_logs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      # Health Check del Contenedor
      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:5000/api/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 15
      }
    }
  ])

  tags = {
    Name = "${var.app_name}-task-definition"
  }
}
```

### 2. ECS Service con Load Balancer

```hcl
# ECS Service con Load Balancer correctamente configurado
resource "aws_ecs_service" "app" {
  name            = "${var.app_name}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnets
    security_groups  = [aws_security_group.ecs_sg.id]
    assign_public_ip = false
  }

  # ✅ Load Balancer - Nombres y puertos deben coincidir exactamente
  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = var.app_name  # Debe coincidir con "name" en container_definitions (ej: "practicas-itm")
    container_port   = 5000           # Debe coincidir con containerPort en portMappings
  }

  depends_on = [
    aws_lb_listener.app_http,
    aws_iam_role_policy_attachment.ecs_task_execution_role_policy
  ]

  tags = {
    Name = "${var.app_name}-service"
  }

  lifecycle {
    ignore_changes = [desired_count]
  }
}
```

### 3. ALB Target Group

```hcl
# ALB Target Group - También debe usar puerto 5000
resource "aws_lb_target_group" "app" {
  name        = "${var.app_name}-tg"
  port        = 5000  # ✅ Debe ser 5000
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"  # IMPORTANTE: "ip" para Fargate

  # Health Check - Apunta al endpoint /api/health
  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/api/health"
    matcher             = "200"
    port                = "5000"
  }

  tags = {
    Name = "${var.app_name}-tg"
  }

  depends_on = [aws_lb.app]
}
```

### 4. Variables que Necesitas (variables.tf)

```hcl
variable "app_name" {
  type        = string
  description = "Application name"
  default     = "practicas-itm"
}

variable "container_image" {
  type        = string
  description = "Container image URI"
  # Ejemplo: "123456789.dkr.ecr.us-east-1.amazonaws.com/practicas-itm:latest"
}

variable "container_port" {
  type        = number
  description = "Container port"
  default     = 5000
}

variable "container_cpu" {
  type        = number
  description = "Container CPU (in CPU units)"
  default     = 256
}

variable "container_memory" {
  type        = number
  description = "Container memory (in MB)"
  default     = 512
}

variable "db_host" {
  type        = string
  description = "Database host"
}

variable "db_port" {
  type        = number
  description = "Database port"
  default     = 5432
}

variable "db_name" {
  type        = string
  description = "Database name"
  default     = "practicas_itm"
}

variable "db_user" {
  type        = string
  description = "Database user"
}

variable "db_password" {
  type        = string
  description = "Database password"
  sensitive   = true
}

variable "vpc_id" {
  type        = string
  description = "VPC ID"
}

variable "private_subnets" {
  type        = list(string)
  description = "Private subnet IDs for ECS tasks"
}

variable "public_subnets" {
  type        = list(string)
  description = "Public subnet IDs for ALB"
}

variable "desired_count" {
  type        = number
  description = "Desired number of tasks"
  default     = 2
}

variable "aws_region" {
  type        = string
  description = "AWS region"
  default     = "us-east-1"
}
```

### 5. terraform.tfvars (Ejemplo)

```hcl
# terraform.tfvars - Tus valores específicos

app_name = "practicas-itm"

# ECR - Reemplaza con tu URI de imagen
container_image = "450328359598.dkr.ecr.us-east-1.amazonaws.com/practicas-itm:latest"

container_port   = 5000
container_cpu    = 256
container_memory = 512

# RDS
db_host     = "tu-rds-endpoint.c2biieuu4rfh.us-east-1.rds.amazonaws.com"
db_port     = 5432
db_name     = "practicas_itm"
db_user     = "practicas_user"
db_password = "tu-password-segura"

# VPC (Reemplaza con tus IDs reales)
vpc_id          = "vpc-xxxxxxxx"
private_subnets = ["subnet-xxxxxxxx", "subnet-yyyyyyyy"]
public_subnets  = ["subnet-zzzzzzzz", "subnet-wwwwwwww"]

desired_count = 2
aws_region    = "us-east-1"
```

## Pasos para Aplicar

### 1. Abre tu repositorio de infraestructura

```bash
cd /path/to/infrastructure/repo
```

### 2. Compara con tu ecs.tf actual

```bash
# Ver la sección actual
grep -A 50 "aws_ecs_task_definition" terraform/ecs.tf | head -60
```

### 3. Reemplaza la sección de container_definitions

Si tu `container_definitions` **NO TIENE** `portMappings`, agrégalo después de `essential = true`:

```hcl
essential = true

# AGREGAR ESTO:
portMappings = [
  {
    containerPort = 5000
    hostPort      = 5000
    protocol      = "tcp"
  }
]
```

### 4. Valida

```bash
terraform fmt -recursive
terraform validate
terraform plan
```

### 5. Aplica

```bash
terraform apply
```

## Lo Que Terraform Hará

1. ✅ Crear una nueva versión de la Task Definition
2. ✅ Actualizar el ECS Service con la nueva versión
3. ✅ Reemplazar las tareas existentes (con rolling update)
4. ✅ El ALB detectará automáticamente las nuevas tareas

## Verificación Posterior

```bash
# Ver la nueva Task Definition
aws ecs describe-task-definition \
  --task-definition practicas-itm \
  --query 'taskDefinition.containerDefinitions[0].portMappings'

# Debe retornar:
# [
#     {
#         "containerPort": 5000,
#         "hostPort": 5000,
#         "protocol": "tcp"
#     }
# ]

# Ver que el servicio está corriendo
aws ecs describe-services \
  --cluster practicas-itm-cluster \
  --services practicas-itm-service \
  --query 'services[0].{Status:status,RunningCount:runningCount,DesiredCount:desiredCount}'

# Ver que los targets están healthy
aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:us-east-1:450328359598:targetgroup/practicas-itm-tg/...
```

## Si Algo Falla

```bash
# Ver logs
aws logs tail /ecs/practicas-itm --follow

# Ver eventos del servicio
aws ecs describe-services \
  --cluster practicas-itm-cluster \
  --services practicas-itm-service \
  --query 'services[0].events' | jq '.[:5]'

# Rollback (eliminar y recrear)
terraform destroy -auto-approve
terraform apply -auto-approve
```

## Cambios Mínimos (Si tu Terraform es muy diferente)

Si tu configuración es completamente diferente, **lo mínimo que necesitas** es agregar `portMappings`:

```hcl
# En container_definitions, después de "image":
portMappings = [
  {
    containerPort = 5000
    hostPort      = 5000
    protocol      = "tcp"
  }
]

# En el ECS Service load_balancer:
container_port = 5000
```

Y asegurar que coincidan los nombres:
- `container_name` en load_balancer = `name` en container_definitions

---

**Eso es todo lo que necesitas para corregir el error.**
