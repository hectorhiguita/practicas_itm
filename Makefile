# Makefile para tareas comunes

.PHONY: help setup install run test test-cov clean db-init db-seed db-reset lint format

help:
	@echo "Comandos disponibles:"
	@echo "  make setup      - Configuración inicial completa"
	@echo "  make install    - Instalar dependencias"
	@echo "  make run        - Ejecutar servidor de desarrollo"
	@echo "  make test       - Ejecutar tests"
	@echo "  make test-cov   - Ejecutar tests con cobertura"
	@echo "  make lint       - Verificar estilo de código"
	@echo "  make format     - Formatear código"
	@echo "  make clean      - Limpiar archivos temporales"
	@echo "  make db-init    - Inicializar base de datos"
	@echo "  make db-seed    - Poblar base de datos"
	@echo "  make db-reset   - Reiniciar base de datos"
	@echo "  make docker-up  - Iniciar con Docker"
	@echo "  make docker-down- Detener Docker"

setup: install db-init db-seed
	@echo "✓ Configuración completada"

install:
	pip install -r requirements.txt

run:
	python main.py

test:
	pytest -v

test-cov:
	pytest --cov=src --cov-report=html
	@echo "✓ Reporte de cobertura: htmlcov/index.html"

lint:
	python -m pylint src/ || true

format:
	python -m black src/ tests/
	python -m isort src/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

db-init:
	python -m src.database.init_db

db-seed:
	python seed_db.py

db-reset:
	python -c "from src.database.connection import engine; from src.models.base import Base; Base.metadata.drop_all(bind=engine)"
	make db-init db-seed

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

.DEFAULT_GOAL := help
