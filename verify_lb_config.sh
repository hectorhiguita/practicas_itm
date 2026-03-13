#!/bin/bash

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Verificación de Configuración del LB${NC}"
echo -e "${BLUE}========================================${NC}\n"

# 1. Verificar que los contenedores están corriendo
echo -e "${YELLOW}1. Verificando estado de los contenedores...${NC}"
if docker ps | grep -q "practicas_itm_api"; then
    echo -e "${GREEN}✓ Contenedor API está corriendo${NC}"
else
    echo -e "${RED}✗ Contenedor API NO está corriendo${NC}"
    exit 1
fi

if docker ps | grep -q "practicas_itm_db"; then
    echo -e "${GREEN}✓ Contenedor BD está corriendo${NC}"
else
    echo -e "${RED}✗ Contenedor BD NO está corriendo${NC}"
    exit 1
fi

# 2. Verificar que el puerto 5000 está expuesto
echo -e "\n${YELLOW}2. Verificando puerto 5000...${NC}"
if docker port practicas_itm_api 2>/dev/null | grep -q "5000"; then
    echo -e "${GREEN}✓ Puerto 5000 está expuesto${NC}"
    docker port practicas_itm_api 2>/dev/null
else
    echo -e "${RED}✗ Puerto 5000 NO está expuesto${NC}"
fi

# 3. Verificar la interfaz de escucha
echo -e "\n${YELLOW}3. Verificando interfaz de escucha (0.0.0.0)...${NC}"
if docker logs practicas_itm_api 2>/dev/null | grep -q "0.0.0.0:5000"; then
    echo -e "${GREEN}✓ La aplicación está escuchando en 0.0.0.0:5000${NC}"
else
    echo -e "${YELLOW}~ No se encuentra referencia explícita (puede estar en los logs de gunicorn)${NC}"
fi

# 4. Verificar el health check
echo -e "\n${YELLOW}4. Verificando health check...${NC}"
HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:5000/api/health 2>/dev/null)
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -1)
BODY=$(echo "$HEALTH_RESPONSE" | head -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Health check respondió con 200${NC}"
    echo -e "${BLUE}  Respuesta: $BODY${NC}"
elif [ "$HTTP_CODE" = "503" ]; then
    echo -e "${YELLOW}⚠ Health check respondió con 503 (BD desconectada)${NC}"
    echo -e "${BLUE}  Respuesta: $BODY${NC}"
else
    echo -e "${RED}✗ Health check respondió con $HTTP_CODE${NC}"
    echo -e "${BLUE}  Respuesta: $BODY${NC}"
fi

# 5. Verificar conectividad a la API
echo -e "\n${YELLOW}5. Verificando conectividad a /api/info...${NC}"
INFO_RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:5000/api/info 2>/dev/null)
HTTP_CODE=$(echo "$INFO_RESPONSE" | tail -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ API info disponible (200)${NC}"
else
    echo -e "${RED}✗ API info no disponible ($HTTP_CODE)${NC}"
fi

# 6. Verificar la red Docker
echo -e "\n${YELLOW}6. Verificando red Docker 'practicas_network'...${NC}"
if docker network ls | grep -q "practicas_network"; then
    echo -e "${GREEN}✓ Red 'practicas_network' existe${NC}"
    echo -e "${BLUE}  Contenedores conectados:${NC}"
    docker network inspect practicas_network 2>/dev/null | grep "\"Name\"" | sed 's/.*"\(.*\)".*/  - \1/'
else
    echo -e "${YELLOW}⚠ Red 'practicas_network' no encontrada (puede estar en default network)${NC}"
fi

# 7. Verificar que Gunicorn está ejecutándose
echo -e "\n${YELLOW}7. Verificando que Gunicorn está ejecutándose...${NC}"
if docker exec practicas_itm_api ps aux 2>/dev/null | grep -q gunicorn; then
    echo -e "${GREEN}✓ Gunicorn está ejecutándose${NC}"
    docker exec practicas_itm_api ps aux 2>/dev/null | grep gunicorn | grep -v grep | awk '{print "  " $0}'
else
    echo -e "${RED}✗ Gunicorn NO está ejecutándose${NC}"
fi

# 8. Verificar variables de entorno
echo -e "\n${YELLOW}8. Verificando variables de entorno...${NC}"
FLASK_ENV=$(docker exec practicas_itm_api env 2>/dev/null | grep "FLASK_ENV" || echo "FLASK_ENV=NOT_SET")
FLASK_DEBUG=$(docker exec practicas_itm_api env 2>/dev/null | grep "FLASK_DEBUG" || echo "FLASK_DEBUG=NOT_SET")
echo -e "${BLUE}  $FLASK_ENV${NC}"
echo -e "${BLUE}  $FLASK_DEBUG${NC}"

# 9. Resumen
echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}Configuración lista para Load Balancer${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo -e "${YELLOW}Próximos pasos:${NC}"
echo "1. Configurar tu Load Balancer para apuntar a:"
echo -e "${BLUE}   http://<contenedor-ip>:5000${NC}"
echo ""
echo "2. Usar el endpoint de health check:"
echo -e "${BLUE}   GET http://<contenedor-ip>:5000/api/health${NC}"
echo ""
echo "3. Para ver logs en tiempo real:"
echo -e "${BLUE}   docker-compose logs -f api${NC}"
echo ""

