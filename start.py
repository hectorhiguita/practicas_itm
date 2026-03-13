#!/usr/bin/env python3
"""
Script de inicio del portal Practicas ITM
"""
import os
import sys
import time

# Agregar directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("🚀 INICIANDO PORTAL PRACTICAS ITM")
print("=" * 60)

# Paso 1: Inicializar BD
print("\n📊 [1/3] Inicializando base de datos...")
try:
    from src.database.connection import init_db
    init_db()
    print("✓ Base de datos lista")
except Exception as e:
    print(f"✗ Error en BD: {e}")
    sys.exit(1)

# Paso 2: Cargar programas
print("\n📚 [2/3] Cargando 32 programas académicos...")
try:
    from src.database.connection import get_session
    from src.models.base import Facultad, Carrera
    db = get_session()
    count = db.query(Carrera).count()
    if count == 0:
        print("ℹ️  Base de datos vacía. Cargando programas...")
        import csv
        facultades_map = {
            'Facultad de Artes y Humanidades': '🎨 Facultad de Artes y Humanidades',
            'Facultad de Ciencias Económicas y Administrativas': '💼 Facultad de Ciencias Económicas y Administrativas',
            'Facultad de Ciencias Exactas y Aplicadas': '🔬 Facultad de Ciencias Exactas y Aplicadas',
            'Facultad de Ingenierías': '⚙️ Facultad de Ingenierías'
        }
        
        # Crear facultades
        facultades_creadas = {}
        for nombre_key, nombre_display in facultades_map.items():
            facultad = db.query(Facultad).filter(Facultad.nombre == nombre_key).first()
            if not facultad:
                facultad = Facultad(nombre=nombre_key)
                db.add(facultad)
            facultades_creadas[nombre_key] = facultad
        db.commit()
        
        # Cargar programas
        with open('PROGRAMAS_ITM.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                facultad_nombre = row['facultad'].strip()
                facultad = facultades_creadas.get(facultad_nombre)
                if facultad:
                    programa = Carrera(
                        nombre=row['programa'].strip(),
                        nivel=row['nivel'].strip(),
                        facultad_id=facultad.id,
                        duracion=row['duracion'].strip(),
                        perfil_profesional=row['perfil_profesional'].strip(),
                        acreditada=1 if row['acreditada'].strip().upper() == 'SI' else 0,
                        virtual=1 if row['virtual'].strip().upper() == 'SI' else 0
                    )
                    db.add(programa)
        db.commit()
    
    count_final = db.query(Carrera).count()
    print(f"✓ {count_final} programas académicos disponibles")
    db.close()
except Exception as e:
    print(f"✗ Error al cargar programas: {e}")

# Paso 3: Iniciar servidor
print("\n🌐 [3/3] Iniciando servidor Flask...")
print("=" * 60)
print("✓ Portal disponible en: http://localhost:5000/")
print("✓ API disponible en: http://localhost:5000/api/")
print("=" * 60)

try:
    from src.api.app import app
    from src.config import get_config
    config = get_config()
    app.run(
        host=config.APP_HOST,
        port=config.APP_PORT,
        debug=config.FLASK_DEBUG
    )
except Exception as e:
    print(f"✗ Error al iniciar servidor: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
