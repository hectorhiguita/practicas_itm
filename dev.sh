#!/bin/bash
# Script de desarrollo para Practicas ITM

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Comandos
case "$1" in
    setup)
        print_header "Configuración Inicial"
        
        print_info "Creando entorno virtual..."
        python3 -m venv venv
        source venv/bin/activate
        print_success "Entorno virtual creado"
        
        print_info "Instalando dependencias..."
        pip install -r requirements.txt
        print_success "Dependencias instaladas"
        
        print_info "Copiando archivo .env..."
        cp .env.example .env
        print_success "Archivo .env creado"
        
        print_info "Inicializando base de datos..."
        python -m src.database.init_db
        print_success "Base de datos inicializada"
        
        print_info "Poblando datos de ejemplo..."
        python seed_db.py
        print_success "Datos de ejemplo cargados"
        
        echo -e "\n${GREEN}✓ Configuración completada${NC}"
        ;;
    
    run)
        print_header "Iniciando Servidor"
        python main.py
        ;;
    
    test)
        print_header "Ejecutando Tests"
        pytest -v
        ;;
    
    test-cov)
        print_header "Ejecutando Tests con Cobertura"
        pytest --cov=src --cov-report=html
        print_success "Reporte de cobertura generado en htmlcov/index.html"
        ;;
    
    db-init)
        print_header "Inicializando Base de Datos"
        python -m src.database.init_db
        ;;
    
    db-seed)
        print_header "Poblando Base de Datos"
        python seed_db.py
        ;;
    
    db-reset)
        print_header "Reiniciando Base de Datos"
        print_info "Eliminando base de datos..."
        python -c "
from src.database.connection import engine
from src.models.base import Base
Base.metadata.drop_all(bind=engine)
print('Base de datos eliminada')
        "
        print_success "Base de datos eliminada"
        
        print_info "Inicializando base de datos..."
        python -m src.database.init_db
        print_success "Base de datos inicializada"
        
        print_info "Poblando con datos de ejemplo..."
        python seed_db.py
        print_success "Datos cargados"
        ;;
    
    lint)
        print_header "Verificando Estilo de Código"
        python -m pylint src/ || true
        ;;
    
    clean)
        print_header "Limpiando Archivos Temporales"
        find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
        find . -type f -name "*.pyc" -delete
        find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
        find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
        print_success "Archivos temporales eliminados"
        ;;
    
    help)
        echo -e "${BLUE}Comandos disponibles:${NC}"
        echo "  setup         - Configuración inicial completa"
        echo "  run           - Iniciar servidor de desarrollo"
        echo "  test          - Ejecutar tests"
        echo "  test-cov      - Ejecutar tests con reporte de cobertura"
        echo "  db-init       - Inicializar base de datos"
        echo "  db-seed       - Poblar base de datos con datos de ejemplo"
        echo "  db-reset      - Reiniciar base de datos completamente"
        echo "  lint          - Verificar estilo de código"
        echo "  clean         - Limpiar archivos temporales"
        echo "  help          - Mostrar esta ayuda"
        ;;
    
    *)
        print_error "Comando no reconocido: $1"
        echo "Usa 'bash dev.sh help' para ver los comandos disponibles"
        exit 1
        ;;
esac
