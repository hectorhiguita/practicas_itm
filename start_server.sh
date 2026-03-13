#!/bin/bash
# Script para iniciar el servidor Practicas ITM

echo "=========================================="
echo "🚀 Iniciando Portal Practicas ITM"
echo "=========================================="

cd /home/hahiguit/Documents/POC/practicas_itm

# Detener cualquier instancia anterior
echo "🛑 Deteniendo instancias anteriores..."
pkill -f "python.*main.py" 2>/dev/null || true
sleep 2

# Activar venv
echo "📦 Activando entorno virtual..."
source .venv/bin/activate

# Iniciar base de datos
echo "🗄️  Inicializando base de datos..."
python -c "from src.database.connection import init_db; init_db()" 2>/dev/null

# Cargar programas
echo "📚 Cargando programas académicos..."
python load_programas.py > /dev/null 2>&1

# Iniciar servidor
echo "🌐 Iniciando servidor en puerto 5000..."
python main.py
