# Configuración del Load Balancer para Practicas ITM

## Estado Actual de la Aplicación

La aplicación está completamente configurada para ser accedida a través de un Load Balancer:

### ✅ Configuración de Red

- **Contenedor**: `practicas_itm_api`
- **Puerto Interno**: `5000`
- **Puerto Expuesto**: `5000`
- **Interfaz**: `0.0.0.0` (escucha en todas las interfaces de red)
- **Protocolo**: HTTP
- **Red Docker**: `practicas_network` (bridge)

### ✅ Servidor de Aplicación

- **Servidor**: Gunicorn (production-ready)
- **Workers**: 2
- **Timeout**: 60 segundos
- **Binding**: `--bind 0.0.0.0:5000`

### ✅ Health Check

La aplicación incluye un endpoint de health check en:

```
GET http://<contenedor-ip>:5000/api/health
```

**Respuesta exitosa (200)**:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

**Respuesta fallida (503)**:
```json
{
  "status": "unhealthy",
  "database": "disconnected"
}
```

## Configuración del Load Balancer

### Para AWS ELB/ALB

```yaml
Listener:
  - Port: 80 (o 443 para HTTPS)
    Protocol: HTTP (o HTTPS)
    Target Group:
      - Port: 5000
        Protocol: HTTP
        Health Check:
          Path: /api/health
          Port: 5000
          Healthy Threshold: 2
          Unhealthy Threshold: 2
          Timeout: 5 seconds
          Interval: 30 seconds
```

### Para NGINX

```nginx
upstream practicas_api {
    server practicas_itm_api:5000;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://practicas_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /api/health {
        proxy_pass http://practicas_api;
        access_log off;
    }
}
```

### Para HAProxy

```haproxy
frontend practicas_frontend
    bind *:80
    default_backend practicas_backend

backend practicas_backend
    balance roundrobin
    server api1 practicas_itm_api:5000 check inter 30s fall 2 rise 2
```

## Puertos Disponibles

| Servicio | Puerto Interno | Puerto Expuesto | Interfaz |
|----------|---|---|---|
| API | 5000 | 5000 | 0.0.0.0 |
| PostgreSQL | 5432 | 5432 | 0.0.0.0 |

## Verificación

### 1. Verificar que el contenedor está corriendo

```bash
docker ps | grep practicas_itm_api
```

### 2. Verificar health check

```bash
curl http://localhost:5000/api/health
```

### 3. Verificar conectividad desde el Load Balancer

```bash
curl -v http://<contenedor-ip>:5000/api/health
```

### 4. Ver logs de la aplicación

```bash
docker logs -f practicas_itm_api
```

### 5. Ver logs de Gunicorn (acceso)

```bash
docker logs practicas_itm_api | grep "GET /api"
```

## Variables de Entorno de Producción

El archivo `.env` debe contener:

```properties
# Base de Datos PostgreSQL (ajustar según tu RDS)
DB_HOST=practicas-itm-db.c2biieuu4rfh.us-east-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=practicas_itm
DB_USER=practicas_user
DB_PASSWORD=tu-password-segura

# Flask (PRODUCCIÓN)
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=tu-secret-key-segura

# Aplicación
APP_HOST=0.0.0.0
APP_PORT=5000
```

## Iniciar los Contenedores

```bash
# Build y start
docker-compose up -d --build

# Verificar estado
docker-compose ps

# Ver logs
docker-compose logs -f api
```

## Escalabilidad

Para escalar a múltiples instancias con Load Balancer:

```bash
# Crear múltiples instancias
docker-compose up -d --scale api=3
```

Ajusta el `docker-compose.yml` para permitir múltiples instancias:

```yaml
api:
  # ... configuración ...
  container_name: practicas_itm_api_${INSTANCE_ID}
  ports:
    - "${PORT}:5000"
```

## Resolución de Problemas

### El Load Balancer no puede alcanzar la aplicación

1. Verificar que el puerto 5000 está expuesto: `docker port practicas_itm_api`
2. Verificar que la aplicación está escuchando en 0.0.0.0: `docker logs practicas_itm_api | grep "Running on"`
3. Verificar permisos de firewall: `sudo iptables -L -n | grep 5000`

### Health check falla

1. Verificar que el endpoint /api/health está disponible: `curl http://localhost:5000/api/health`
2. Verificar que la base de datos está conectada: `docker logs practicas_itm_api`
3. Revisar logs de PostgreSQL: `docker logs practicas_itm_db`

### Conexión a la base de datos falla

1. Verificar credenciales en el docker-compose.yml
2. Verificar que el contenedor de PostgreSQL está sano: `docker-compose ps`
3. Revisar logs: `docker-compose logs postgres`

## Notas Importantes

- ✅ La aplicación ya está configurada para producción en el Dockerfile
- ✅ Gunicorn se ejecuta automáticamente con el Dockerfile
- ✅ El docker-compose.yml utiliza la configuración de producción
- ✅ Health check está implementado y disponible
- ✅ La aplicación escucha en 0.0.0.0:5000 (accesible desde la red)
- ✅ Reinicio automático habilitado (restart: unless-stopped)
