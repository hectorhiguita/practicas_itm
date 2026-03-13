#!/bin/bash

# Script para validar la configuración de Terraform para el LB de Practicas ITM
# Este script verifica que la Task Definition tiene el puerto 5000 correctamente configurado

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Validador de Configuración ECS${NC}"
echo -e "${BLUE}================================${NC}\n"

# Verificar que estamos en el directorio correcto
if [ ! -f "terraform/ecs.tf" ]; then
    echo -e "${RED}✗ No se encontró terraform/ecs.tf${NC}"
    echo "Por favor ejecuta este script desde la raíz del repositorio de infraestructura"
    exit 1
fi

echo -e "${YELLOW}1. Buscando portMappings en ecs.tf...${NC}"
if grep -q "portMappings" terraform/ecs.tf; then
    echo -e "${GREEN}✓ portMappings encontrado${NC}"
    grep -A 5 "portMappings" terraform/ecs.tf | head -6
else
    echo -e "${RED}✗ portMappings NO encontrado${NC}"
    echo "   Necesitas agregar portMappings a la Task Definition"
fi

echo -e "\n${YELLOW}2. Verificando que container_port es 5000...${NC}"
if grep -q 'container_port.*=.*5000' terraform/ecs.tf; then
    echo -e "${GREEN}✓ container_port = 5000 encontrado${NC}"
else
    echo -e "${YELLOW}⚠ Verificar manualmente que container_port = 5000${NC}"
    grep "container_port" terraform/ecs.tf || echo "   No encontrado"
fi

echo -e "\n${YELLOW}3. Buscando el nombre del contenedor...${NC}"
CONTAINER_NAME=$(grep -o '"name".*"practicas-itm"' terraform/ecs.tf | head -1)
if [ ! -z "$CONTAINER_NAME" ]; then
    echo -e "${GREEN}✓ Nombre del contenedor encontrado${NC}"
    echo "   $CONTAINER_NAME"
else
    echo -e "${YELLOW}⚠ No se encontró el nombre exacto del contenedor${NC}"
    echo "   Asegúrate de que sea 'practicas-itm'"
fi

echo -e "\n${YELLOW}4. Validando coherencia entre Task Definition y Service...${NC}"
TASK_PORT=$(grep -A 10 "portMappings" terraform/ecs.tf | grep "containerPort" | head -1 | grep -o '[0-9]*')
SERVICE_PORT=$(grep -A 2 "load_balancer {" terraform/ecs.tf | grep "container_port" | grep -o '[0-9]*')

if [ ! -z "$TASK_PORT" ] && [ ! -z "$SERVICE_PORT" ]; then
    if [ "$TASK_PORT" = "$SERVICE_PORT" ]; then
        echo -e "${GREEN}✓ Los puertos coinciden (ambos $TASK_PORT)${NC}"
    else
        echo -e "${RED}✗ Los puertos NO coinciden${NC}"
        echo "   Task Definition: $TASK_PORT"
        echo "   Service: $SERVICE_PORT"
    fi
else
    echo -e "${YELLOW}⚠ No se pudieron extraer los puertos${NC}"
fi

echo -e "\n${YELLOW}5. Revisando variables en terraform.tfvars...${NC}"
if [ -f "terraform.tfvars" ]; then
    if grep -q "container_port.*=.*5000" terraform.tfvars; then
        echo -e "${GREEN}✓ terraform.tfvars tiene container_port = 5000${NC}"
    else
        echo -e "${YELLOW}⚠ Verificar container_port en terraform.tfvars${NC}"
        grep "container_port" terraform.tfvars || echo "   No encontrado"
    fi
else
    echo -e "${YELLOW}⚠ terraform.tfvars no encontrado${NC}"
fi

echo -e "\n${YELLOW}6. Ejecutando terraform validate...${NC}"
if terraform validate > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Configuración de Terraform es válida${NC}"
else
    echo -e "${RED}✗ Hay errores en la configuración de Terraform${NC}"
    terraform validate
fi

echo -e "\n${YELLOW}7. Resumen de lo que necesita estar configurado...${NC}"
echo -e "${BLUE}En task_definition:${NC}"
echo "  - name: practicas-itm"
echo "  - portMappings[0].containerPort: 5000"
echo "  - portMappings[0].hostPort: 5000"
echo ""
echo -e "${BLUE}En ecs_service load_balancer:${NC}"
echo "  - container_name: practicas-itm"
echo "  - container_port: 5000"
echo ""
echo -e "${BLUE}En lb_target_group:${NC}"
echo "  - port: 5000"
echo "  - health_check.port: 5000"

echo -e "\n${BLUE}================================${NC}"
echo -e "${GREEN}Validación completada${NC}"
echo -e "${BLUE}================================${NC}\n"

echo -e "${YELLOW}Si hay errores, ejecuta:${NC}"
echo "  terraform plan"
echo "  terraform apply"
