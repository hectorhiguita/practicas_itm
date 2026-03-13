#!/usr/bin/env python3
"""
Script para cargar programas académicos ITM desde CSV a la base de datos
"""
import csv
import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.connection import get_session, init_db
from src.models.base import Facultad, Carrera
from src.services.programa_service import ProgramaService

def cargar_programas_desde_csv():
    """
    Carga todos los programas académicos desde PROGRAMAS_ITM.csv
    """
    print("=" * 70)
    print("CARGADOR DE PROGRAMAS ACADÉMICOS ITM")
    print("=" * 70)
    
    # Inicializar base de datos
    print("\n📊 Inicializando base de datos...")
    try:
        init_db()
        print("✓ Base de datos inicializada")
    except Exception as e:
        print(f"✗ Error al inicializar BD: {e}")
        return
    
    db = get_session()
    
    try:
        # Crear facultades
        facultades_map = {
            'Facultad de Artes y Humanidades': '🎨 Facultad de Artes y Humanidades',
            'Facultad de Ciencias Económicas y Administrativas': '💼 Facultad de Ciencias Económicas y Administrativas',
            'Facultad de Ciencias Exactas y Aplicadas': '🔬 Facultad de Ciencias Exactas y Aplicadas',
            'Facultad de Ingenierías': '⚙️ Facultad de Ingenierías'
        }
        
        facultades_creadas = {}
        print("\n📚 Creando/verificando facultades...")
        
        for nombre_key, nombre_display in facultades_map.items():
            facultad = db.query(Facultad).filter(Facultad.nombre == nombre_key).first()
            
            if not facultad:
                facultad = Facultad(nombre=nombre_key)
                db.add(facultad)
                db.flush()
                print(f"  ✓ Creada: {nombre_display}")
            else:
                print(f"  → Existe: {nombre_display}")
            
            facultades_creadas[nombre_key] = facultad
        
        db.commit()
        
        # Cargar programas desde CSV
        print("\n📖 Cargando programas desde CSV...")
        csv_path = 'PROGRAMAS_ITM.csv'
        
        if not os.path.exists(csv_path):
            print(f"✗ Archivo {csv_path} no encontrado")
            return
        
        programas_cargados = 0
        programas_duplicados = 0
        programas_error = 0
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    facultad_nombre = row['facultad'].strip()
                    programa_nombre = row['programa'].strip()
                    nivel = row['nivel'].strip()
                    duracion = row['duracion'].strip()
                    perfil = row['perfil_profesional'].strip()
                    acreditada = row['acreditada'].strip().upper() == 'SI'
                    virtual = row['virtual'].strip().upper() == 'SI'
                    
                    # Obtener facultad
                    facultad = facultades_creadas.get(facultad_nombre)
                    if not facultad:
                        print(f"  ✗ Facultad no encontrada: {facultad_nombre}")
                        programas_error += 1
                        continue
                    
                    # Verificar si el programa ya existe
                    programa_existe = db.query(Carrera).filter(
                        Carrera.nombre == programa_nombre,
                        Carrera.facultad_id == facultad.id
                    ).first()
                    
                    if programa_existe:
                        programas_duplicados += 1
                        continue
                    
                    # Crear programa
                    programa = Carrera(
                        nombre=programa_nombre,
                        nivel=nivel,
                        facultad_id=facultad.id,
                        duracion=duracion,
                        perfil_profesional=perfil,
                        acreditada=1 if acreditada else 0,
                        virtual=1 if virtual else 0
                    )
                    
                    db.add(programa)
                    programas_cargados += 1
                    
                except Exception as e:
                    print(f"  ✗ Error procesando fila: {e}")
                    programas_error += 1
                    continue
        
        db.commit()
        
        # Mostrar estadísticas
        print("\n📊 ESTADÍSTICAS DE CARGA:")
        print(f"  ✓ Programas cargados: {programas_cargados}")
        print(f"  → Programas duplicados: {programas_duplicados}")
        print(f"  ✗ Errores: {programas_error}")
        
        # Mostrar resumen por facultad y nivel
        print("\n📈 RESUMEN POR FACULTAD Y NIVEL:")
        
        for nombre_key, nombre_display in facultades_map.items():
            facultad = facultades_creadas[nombre_key]
            total = db.query(Carrera).filter(Carrera.facultad_id == facultad.id).count()
            
            if total > 0:
                print(f"\n  {nombre_display}")
                
                for nivel in ['Tecnología', 'Profesional', 'Ingeniería']:
                    count = db.query(Carrera).filter(
                        Carrera.facultad_id == facultad.id,
                        Carrera.nivel == nivel
                    ).count()
                    
                    if count > 0:
                        print(f"    • {nivel}: {count} programa(s)")
        
        # Estadísticas generales
        stats = ProgramaService.obtener_estadisticas_programas(db)
        print("\n📊 ESTADÍSTICAS GENERALES:")
        print(f"  Total de programas: {stats['total_programas']}")
        print(f"  Programas acreditados: {stats['total_acreditados']}")
        print(f"  Programas virtuales: {stats['total_virtuales']}")
        print(f"  Por nivel:")
        print(f"    • Tecnología: {stats['por_nivel']['Tecnología']}")
        print(f"    • Profesional: {stats['por_nivel']['Profesional']}")
        print(f"    • Ingeniería: {stats['por_nivel']['Ingeniería']}")
        
        print("\n" + "=" * 70)
        print("✓ CARGA COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error fatal: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    cargar_programas_desde_csv()
