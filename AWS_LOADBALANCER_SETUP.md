# Configuración de Load Balancer en AWS para Practicas ITM

## Información del Contenedor

```
Nombre: practicas_itm_api
Puerto Interno: 5000
Puerto Expuesto: 5000
Protocolo: HTTP
Interfaz: 0.0.0.0 (todas las interfaces)
```

## Pasos para Configurar el ALB/ELB en AWS

### 1. Crear Target Group

En AWS EC2 → Target Groups:

```
Name: practicas-itm-tg
Protocol: HTTP
Port: 5000
VPC: <tu-vpc>
Health Check:
  ├─ Protocol: HTTP
  ├─ Path: /api/health
  ├─ Port: 5000
  ├─ Healthy Threshold: 2
  ├─ Unhealthy Threshold: 2
  ├─ Timeout: 5 seconds
  ├─ Interval: 30 seconds
  └─ Success Codes: 200
```

### 2. Registrar Targets

En el Target Group, agregar el contenedor:

```
Instance: <instancia-ec2>
Port: 5000
```

O si usas ECS:

```
Container: practicas_itm_api
Port: 5000
```

### 3. Crear o Actualizar el Application Load Balancer

```
Name: practicas-itm-alb
Scheme: internet-facing (o internal según necesidad)
Listeners:
  └─ Port 80 → HTTP
      └─ Target Group: practicas-itm-tg
```

O si usas HTTPS:

```
Port 443 → HTTPS (con certificado SSL/TLS)
  └─ Target Group: practicas-itm-tg
Port 80 → HTTP (redirigir a 443)
```

### 4. Configurar Security Groups

**Para el ALB:**
```
Inbound Rules:
  ├─ HTTP (80) desde Anywhere (0.0.0.0/0)
  └─ HTTPS (443) desde Anywhere (0.0.0.0/0) [opcional]

Outbound Rules:
  └─ All traffic hacia Security Group de la instancia EC2
```

**Para la instancia EC2 donde corre el contenedor:**
```
Inbound Rules:
  ├─ HTTP (5000) desde ALB Security Group
  └─ SSH (22) desde tu IP [para administración]

Outbound Rules:
  ├─ All traffic (para actualizar paquetes, etc)
  └─ PostgreSQL (5432) hacia RDS [si es necesario]
```

### 5. Configurar la Instancia EC2

**Instalar Docker y Docker Compose:**

```bash
#!/bin/bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
sudo apt-get install -y docker.io
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Start Docker daemon
sudo systemctl start docker
sudo systemctl enable docker
```

**Clonar y configurar la aplicación:**

```bash
# Clone repository
git clone <repo-url> /opt/practicas_itm
cd /opt/practicas_itm

# Create .env file with your configuration
cat > .env << EOF
DB_HOST=tu-rds-endpoint.c2biieuu4rfh.us-east-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=practicas_itm
DB_USER=practicas_user
DB_PASSWORD=tu-password
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=tu-secret-key
APP_HOST=0.0.0.0
APP_PORT=5000
EOF

# Build and start containers
docker-compose up -d

# Verify
docker-compose ps
curl http://localhost:5000/api/health
```

### 6. Verificar que el ALB puede alcanzar el contenedor

Desde la instancia EC2:

```bash
# El contenedor debe ser alcanzable
curl http://localhost:5000/api/health

# Verificar que está escuchando en todas las interfaces
docker exec practicas_itm_api netstat -tlnp | grep 5000
```

Respuesta esperada:
```
tcp        0      0 0.0.0.0:5000            0.0.0.0:*               LISTEN      -
```

### 7. Monitoreo en AWS CloudWatch

**Ver logs del ALB:**

```
AWS Console → EC2 → Load Balancers → practicas-itm-alb
→ Monitoring → View Load Balancer Metrics
```

**Ver logs de la aplicación:**

```bash
# En la instancia EC2
docker logs -f practicas_itm_api

# O con CloudWatch
docker run -d \
  --log-driver awslogs \
  --log-opt awslogs-group=/ecs/practicas_itm \
  --log-opt awslogs-region=us-east-1 \
  --log-opt awslogs-stream-prefix=ecs \
  practicas_itm_api
```

## Verificación de Conectividad

### Desde local (con SSH tunnel)

```bash
# Port forward
ssh -i your-key.pem -L 5000:localhost:5000 ec2-user@your-ec2-ip

# Luego acceder
curl http://localhost:5000/api/health
```

### Desde el ALB DNS

```bash
# Obtener DNS del ALB
ALB_DNS=$(aws elbv2 describe-load-balancers \
  --names practicas-itm-alb \
  --query 'LoadBalancers[0].DNSName' \
  --output text)

# Acceder a través del ALB
curl http://$ALB_DNS/api/health
```

## Solución de Problemas

### El ALB no puede alcanzar el contenedor

1. **Verificar health check:**

```bash
# En la instancia EC2
curl -v http://localhost:5000/api/health

# Debe retornar 200 o 503 (no 404 o 502)
```

2. **Verificar que el puerto está abierto:**

```bash
# En la instancia EC2
sudo netstat -tlnp | grep 5000
# O
docker port practicas_itm_api
```

3. **Verificar Security Groups:**

```bash
# Asegurar que el ALB SG puede hablar al EC2 SG en puerto 5000
# AWS Console → Security Groups → Inbound Rules
```

4. **Ver logs del ALB:**

```bash
# AWS Console → EC2 → Load Balancers → Monitoring
# Revisar "Target Response Time" y "HTTP 5xx/4xx"
```

### El contenedor no inicia

```bash
# Ver logs
docker logs practicas_itm_api

# Verificar que la BD está disponible
docker-compose ps

# Revisar conexión a RDS
docker exec practicas_itm_api python -c "
import psycopg2
conn = psycopg2.connect('dbname=practicas_itm user=practicas_user password=XXX host=XXX')
print('BD Conectada')
"
```

### Health check falla pero la app responde

1. Aumentar el timeout en el Target Group a 10 segundos
2. Verificar que `/api/health` está disponible:

```bash
curl -v http://localhost:5000/api/health
```

3. Revisar que la base de datos está conectada:

```bash
docker logs practicas_itm_api | grep "database\|connected"
```

## Variables de Entorno para Producción

Actualizar el `.env` con tus valores:

```properties
# Base de Datos RDS de AWS
DB_HOST=tu-rds-endpoint.c2biieuu4rfh.us-east-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=practicas_itm
DB_USER=admin_user
DB_PASSWORD=tu_password_segura_aqui

# Flask - PRODUCCIÓN
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=generate-a-secure-random-key-here

# Aplicación
APP_HOST=0.0.0.0
APP_PORT=5000
```

## Autoescalado (Escalabilidad Horizontal)

### Con EC2 Auto Scaling Group

1. Crear una AMI con la aplicación
2. Crear Launch Template con el User Data
3. Crear Auto Scaling Group
4. Configurar política de escalado

### Con ECS (Recomendado)

```json
{
  "cluster": "practicas-itm-cluster",
  "serviceName": "practicas-itm-service",
  "desiredCount": 2,
  "launchType": "EC2",
  "taskDefinition": "practicas-itm-task",
  "loadBalancers": [{
    "targetGroupArn": "arn:aws:...:targetgroup/practicas-itm-tg/...",
    "containerName": "practicas_itm_api",
    "containerPort": 5000
  }],
  "autoScalingGroupProvider": {
    "autoScalingGroupArn": "arn:aws:autoscaling:...",
    "managedScaling": {
      "status": "ENABLED",
      "targetCapacity": 80
    }
  }
}
```

## Comandos Útiles de AWS CLI

```bash
# Describir ALB
aws elbv2 describe-load-balancers --names practicas-itm-alb

# Ver estado de targets
aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:...

# Ver métricas del ALB
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name TargetResponseTime \
  --dimensions Name=LoadBalancer,Value=app/practicas-itm-alb/... \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 300 \
  --statistics Average,Maximum
```

## Resumen

✅ **Aplicación configurada para:**
- Escuchar en `0.0.0.0:5000` (accesible desde la red)
- Usar Gunicorn como servidor (production-ready)
- Incluir health check en `/api/health`
- Configuración de producción

✅ **Load Balancer debe:**
- Apuntar a puerto `5000`
- Usar health check en `/api/health`
- Tener timeout mínimo de 30 segundos en health check
- Estar en la misma VPC o con conectividad

✅ **Security:**
- ALB en puertos 80/443
- Instancia EC2 solo acepta 5000 desde ALB SG
- RDS en red privada con credenciales seguras
