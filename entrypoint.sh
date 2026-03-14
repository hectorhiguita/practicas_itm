#!/bin/sh
set -e

echo "=== Inicializando base de datos ==="
python -c "from src.database.init_db import init_database; init_database()"
echo "=== Base de datos lista. Iniciando servidor ==="

# SKIP_DB_INIT=1 evita que cada worker repita la inicialización al importar el módulo
exec env SKIP_DB_INIT=1 gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    src.api.app:app
