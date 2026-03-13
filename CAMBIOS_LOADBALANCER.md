# Resumen de Cambios - Configuración para Load Balancer

## 📋 Cambios Realizados

### 1. **docker-compose.yml** (ACTUALIZADO)

#### Cambios principales:

**Antes:**
```yaml
command: python main.py
environment:
  FLASK_ENV: development
  FLASK_DEBUG: True
volumes:
  - .:/app
```

**Después:**
```yaml
# Se usa el comando de Gunicorn del Dockerfile (production-ready)
environment:
  FLASK_ENV: production
  FLASK_DEBUG: False
healthcheck:
  test: ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')\" || exit 1"]
  interval: 30s
  timeout: 5s
  retries: 3
  start_period: 15s
networks:
  - practicas_network
restart: unless-stopped
```

✅ **Beneficios:**
- Servidor production-ready (Gunicorn)
- Health check implementado
- Configuración optimizada para LB
- Red Docker explícita
- Reinicio automático en fallos

---

### 2. **Dockerfile** (SIN CAMBIOS)

El Dockerfile ya estaba correctamente configurado:

```dockerfile
# Gunicorn corriendo en 0.0.0.0:5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "60", "--access-logfile", "-", "src.api.app:app"]
```

✅ **Ya configurable:**
- 2 workers de Gunicorn
- Escucha en todas las interfaces (0.0.0.0)
- Puerto 5000 expuesto
- Health check implementado

---

### 3. **Nuevos Archivos Creados**

#### A. `LOADBALANCER_CONFIG.md`
Documentación completa sobre:
- Configuración actual de la red
- Endpoints disponibles
- Ejemplos para AWS ALB, NGINX, HAProxy
- Health check
- Verificación y troubleshooting

#### B. `AWS_LOADBALANCER_SETUP.md`
Guía paso a paso para AWS:
- Crear Target Group
- Configurar ALB
- Security Groups
- User Data para instancias EC2
- Verificación y monitoreo
- Solución de problemas
- Comandos AWS CLI

#### C. `docker-compose.prod.yml`
Configuración para producción con:
- 3 instancias de la API en paralelo
- PostgreSQL compartida
- Puertos expuestos (5001, 5002, 5003)
- Health checks completos
- Red Docker dedicada

#### D. `nginx.conf`
Configuración de NGINX como Load Balancer local:
- Upstream con 3 servidores
- Round-robin balancing
- Proxy headers completos
- SSL/TLS ready
- Compresión GZIP
- Health endpoint

#### E. `verify_lb_config.sh`
Script de verificación (ejecutable):
```bash
./verify_lb_config.sh
```
Verifica:
- Estado de contenedores
- Puertos expuestos
- Health check
- Interfaz de escucha
- Red Docker
- Gunicorn ejecutándose
- Variables de entorno

---

## 🎯 Arquitectura Resultante

```
┌─────────────────────────────────────────────────────┐
│              LOAD BALANCER (AWS ALB)                │
│                   :80 / :443                        │
└──────────────────────┬──────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
  │  API Pod 1  │ │  API Pod 2  │ │  API Pod 3  │
  │  :5000      │ │  :5000      │ │  :5000      │
  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
                  ┌──────▼──────┐
                  │ PostgreSQL  │
                  │   :5432     │
                  └─────────────┘
```

---

## 📌 Puntos Clave de la Configuración

### 1. **Puerto 5000**
✅ La aplicación escucha en `0.0.0.0:5000`
✅ Accesible desde la red interna
✅ El Load Balancer apunta a este puerto

### 2. **Health Check**
✅ Endpoint: `GET /api/health`
✅ Intervalo: 30 segundos
✅ Timeout: 5 segundos
✅ Responde con estado de BD

### 3. **Servidor Web**
✅ Gunicorn (production-ready)
✅ 2 workers
✅ Timeout: 60 segundos
✅ Logs en stdout

### 4. **Red**
✅ Red Docker: `practicas_network`
✅ Comunicación interna entre contenedores
✅ Expuesto al host en puerto 5000

---

## 🚀 Cómo Usar

### Opción 1: Single Instance (Actual)

```bash
cd /home/hahiguit/Documents/POC/practicas_itm

# Iniciar
docker-compose up -d

# Verificar
./verify_lb_config.sh

# Acceder
curl http://localhost:5000/api/health
```

### Opción 2: Multiple Instances (Para Escalado)

```bash
# Iniciar 3 instancias
docker-compose -f docker-compose.prod.yml up -d

# Verificar
docker-compose -f docker-compose.prod.yml ps

# Acceder a cada instancia
curl http://localhost:5001/api/health  # API 1
curl http://localhost:5002/api/health  # API 2
curl http://localhost:5003/api/health  # API 3
```

### Opción 3: Con NGINX Load Balancer Local

```bash
# Descomenta la sección nginx en docker-compose.prod.yml
# Luego:

docker-compose -f docker-compose.prod.yml up -d

# Acceder a través del LB
curl http://localhost:80/api/health
```

---

## ✅ Verificación de Disponibilidad para LB

### Health Check

```bash
# Debe retornar 200 o 503 (no 404 o 502)
curl -v http://localhost:5000/api/health

# Respuesta exitosa:
# HTTP/1.1 200 OK
# {"status": "healthy", "database": "connected"}
```

### API Info

```bash
curl http://localhost:5000/api/info
```

### Logs

```bash
# Ver logs en tiempo real
docker-compose logs -f api

# Ver solo errores
docker-compose logs api | grep ERROR
```

---

## 📊 Variables de Entorno

### Desarrollo (Local)
```properties
FLASK_ENV=development
FLASK_DEBUG=True
DB_HOST=localhost
```

### Producción (Docker/LB)
```properties
FLASK_ENV=production
FLASK_DEBUG=False
DB_HOST=postgres  # O RDS endpoint
APP_HOST=0.0.0.0
APP_PORT=5000
```

---

## 🔒 Security Best Practices

1. **Nunca exponer en desarrollo:**
   - ✅ `FLASK_DEBUG=False` en producción
   - ✅ `SECRET_KEY` único y seguro
   - ✅ BD con credenciales fuertes

2. **Network:**
   - ✅ ALB solo en puertos 80/443
   - ✅ API solo accesible desde ALB
   - ✅ BD en red privada

3. **Health Check:**
   - ✅ No requiere autenticación
   - ✅ Endpoint público pero sin datos sensibles
   - ✅ Indica estado de BD

---

## 📝 Próximos Pasos

### Para AWS ALB

1. Crear Target Group apuntando a puerto 5000
2. Configurar Health Check en `/api/health`
3. Crear ALB en los puertos 80/443
4. Registrar las instancias EC2 en el Target Group
5. Verificar con Script: `./verify_lb_config.sh`

### Para Escalado

1. Copiar `docker-compose.prod.yml` para 3+ instancias
2. Configurar NGINX con upstream definido
3. O usar AWS Auto Scaling Group

### Para HTTPS

1. Obtener certificado SSL (Let's Encrypt)
2. Configurar NGINX/ALB con SSL
3. Redirigir HTTP → HTTPS
4. Descomentar secciones SSL en nginx.conf

---

## 📞 Comandos Útiles

```bash
# Verificar
./verify_lb_config.sh

# Logs
docker-compose logs -f api

# Ejecutar comando en contenedor
docker exec practicas_itm_api /bin/bash

# Reiniciar
docker-compose restart api

# Reconstruir
docker-compose up -d --build

# Parar
docker-compose down

# Estadísticas
docker stats practicas_itm_api
```

---

## 🎉 Resumen Final

La aplicación está **lista para ser integrada con un Load Balancer**:

✅ Escucha en `0.0.0.0:5000`
✅ Gunicorn configurado correctamente
✅ Health check disponible
✅ Docker Compose optimizado
✅ Documentación completa
✅ Script de verificación
✅ Ejemplos para AWS, NGINX, HAProxy
✅ Configuración multi-instancia lista

**Solo necesitas apuntar tu Load Balancer al puerto 5000 de tu instancia EC2 y comenzará a funcionar.**
