#!/usr/bin/env python3
"""
Script de prueba para demonstrar el API de Programas Académicos
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.connection import get_session
from src.services.programa_service import ProgramaService
from src.models.base import Carrera, Facultad

def demostrar_api_programas():
    """Demuestra las funcionalidades del servicio de programas"""
    
    db = get_session()
    
    print("\n" + "=" * 80)
    print("DEMOSTRACIÓN - API DE PROGRAMAS ACADÉMICOS ITM")
    print("=" * 80)
    
    try:
        # 1. Obtener todos los programas
        print("\n1️⃣  OBTENER TODOS LOS PROGRAMAS")
        print("-" * 80)
        todos = ProgramaService.obtener_todos_programas(db)
        print(f"Total de programas: {len(todos)}")
        print("\nPrimeros 5 programas:")
        for i, prog in enumerate(todos[:5], 1):
            print(f"  {i}. {prog.nombre} ({prog.nivel})")
        
        # 2. Obtener programas por nivel
        print("\n2️⃣  OBTENER PROGRAMAS POR NIVEL")
        print("-" * 80)
        for nivel in ['Tecnología', 'Profesional', 'Ingeniería']:
            programas = ProgramaService.obtener_programas_por_nivel(db, nivel)
            print(f"  • {nivel}: {len(programas)} programas")
        
        # 3. Obtener programas acreditados
        print("\n3️⃣  OBTENER PROGRAMAS ACREDITADOS")
        print("-" * 80)
        acreditados = ProgramaService.obtener_programas_acreditados(db)
        print(f"Total acreditados: {len(acreditados)}")
        print("\nEjemplos de programas acreditados:")
        for prog in acreditados[:3]:
            print(f"  • {prog.nombre} ({prog.facultad.nombre})")
        
        # 4. Obtener programas virtuales
        print("\n4️⃣  OBTENER PROGRAMAS VIRTUALES")
        print("-" * 80)
        virtuales = ProgramaService.obtener_programas_virtuales(db)
        print(f"Total virtuales: {len(virtuales)}")
        print("\nProgramas virtuales:")
        for prog in virtuales:
            print(f"  • {prog.nombre} ({prog.facultad.nombre})")
        
        # 5. Obtener por facultad
        print("\n5️⃣  OBTENER PROGRAMAS POR FACULTAD")
        print("-" * 80)
        facultades = db.query(Facultad).all()
        for fac in facultades:
            progs = ProgramaService.obtener_todos_programas(db, facultad_id=fac.id)
            print(f"\n  {fac.nombre}: {len(progs)} programas")
            for prog in progs[:2]:
                acred = "✓ Acreditado" if prog.acreditada else ""
                virt = "- Virtual" if prog.virtual else ""
                print(f"    • {prog.nombre} {acred} {virt}")
            if len(progs) > 2:
                print(f"    • ... y {len(progs) - 2} más")
        
        # 6. Estadísticas
        print("\n6️⃣  ESTADÍSTICAS GENERALES")
        print("-" * 80)
        stats = ProgramaService.obtener_estadisticas_programas(db)
        print(f"\nTotal de programas: {stats['total_programas']}")
        print(f"Acreditados: {stats['total_acreditados']} ({stats['total_acreditados']*100//stats['total_programas']}%)")
        print(f"Virtuales: {stats['total_virtuales']} ({stats['total_virtuales']*100//stats['total_programas']}%)")
        print(f"\nPor nivel:")
        for nivel, count in stats['por_nivel'].items():
            pct = count * 100 // stats['total_programas']
            print(f"  • {nivel}: {count} ({pct}%)")
        
        # 7. Ejemplo de programa específico
        print("\n7️⃣  OBTENER PROGRAMA POR ID")
        print("-" * 80)
        primer_programa = ProgramaService.obtener_todos_programas(db)[0]
        print(f"\nPrograma: {primer_programa.id}")
        print(f"  Nombre: {primer_programa.nombre}")
        print(f"  Facultad: {primer_programa.facultad.nombre}")
        print(f"  Nivel: {primer_programa.nivel}")
        print(f"  Duración: {primer_programa.duracion}")
        print(f"  Acreditado: {'Sí' if primer_programa.acreditada else 'No'}")
        print(f"  Virtual: {'Sí' if primer_programa.virtual else 'No'}")
        print(f"  Perfil: {primer_programa.perfil_profesional[:80]}...")
        
        # 8. Exportar como JSON
        print("\n8️⃣  EXPORTAR A JSON")
        print("-" * 80)
        programa_dict = primer_programa.to_dict()
        print(f"\nJSON del primer programa:")
        print(json.dumps(programa_dict, indent=2, ensure_ascii=False))
        
        print("\n" + "=" * 80)
        print("✓ DEMOSTRACIÓN COMPLETADA")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    demostrar_api_programas()
