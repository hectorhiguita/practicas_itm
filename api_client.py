#!/usr/bin/env python3
"""
Script de cliente para probar la API
Uso: python api_client.py <comando> [argumentos]
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Configuración
BASE_URL = "http://localhost:5000/api"

class APIClient:
    """Cliente para interactuar con la API"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def _print_response(self, response: requests.Response):
        """Imprime la respuesta formateada"""
        print(f"\n📊 Status: {response.status_code}")
        try:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except:
            print(response.text)
    
    # FACULTADES
    def crear_facultad(self, nombre: str, descripcion: str = None):
        """Crear una facultad"""
        data = {"nombre": nombre}
        if descripcion:
            data["descripcion"] = descripcion
        
        response = self.session.post(f"{self.base_url}/facultades/", json=data)
        self._print_response(response)
    
    def listar_facultades(self):
        """Listar todas las facultades"""
        response = self.session.get(f"{self.base_url}/facultades/")
        self._print_response(response)
    
    def obtener_facultad(self, facultad_id: int):
        """Obtener una facultad por ID"""
        response = self.session.get(f"{self.base_url}/facultades/{facultad_id}")
        self._print_response(response)
    
    # CARRERAS
    def crear_carrera(self, nombre: str, facultad_id: int, descripcion: str = None):
        """Crear una carrera"""
        data = {
            "nombre": nombre,
            "facultad_id": facultad_id
        }
        if descripcion:
            data["descripcion"] = descripcion
        
        response = self.session.post(f"{self.base_url}/carreras/", json=data)
        self._print_response(response)
    
    def listar_carreras(self, facultad_id: int = None):
        """Listar carreras"""
        params = {}
        if facultad_id:
            params["facultad_id"] = facultad_id
        
        response = self.session.get(f"{self.base_url}/carreras/", params=params)
        self._print_response(response)
    
    # ESTUDIANTES
    def crear_estudiante(self, numero_documento: str, nombre: str, apellido: str,
                        email: str, genero: str, facultad_id: int, carrera_id: int,
                        telefono: str = None):
        """Crear un estudiante"""
        data = {
            "numero_documento": numero_documento,
            "nombre": nombre,
            "apellido": apellido,
            "email": email,
            "genero": genero,
            "facultad_id": facultad_id,
            "carrera_id": carrera_id
        }
        if telefono:
            data["telefono"] = telefono
        
        response = self.session.post(f"{self.base_url}/estudiantes/", json=data)
        self._print_response(response)
    
    def listar_estudiantes(self, facultad_id: int = None, carrera_id: int = None,
                          estado: str = None):
        """Listar estudiantes"""
        params = {}
        if facultad_id:
            params["facultad_id"] = facultad_id
        if carrera_id:
            params["carrera_id"] = carrera_id
        if estado:
            params["estado"] = estado
        
        response = self.session.get(f"{self.base_url}/estudiantes/", params=params)
        self._print_response(response)
    
    def listar_disponibles(self):
        """Listar estudiantes disponibles"""
        response = self.session.get(f"{self.base_url}/estudiantes/disponibles")
        self._print_response(response)
    
    def obtener_estudiante(self, estudiante_id: int):
        """Obtener un estudiante por ID"""
        response = self.session.get(f"{self.base_url}/estudiantes/{estudiante_id}")
        self._print_response(response)
    
    def actualizar_estado(self, estudiante_id: int, estado: str):
        """Actualizar estado de práctica"""
        data = {"estado": estado}
        response = self.session.put(f"{self.base_url}/estudiantes/{estudiante_id}/estado", json=data)
        self._print_response(response)
    
    def estadisticas_facultad(self, facultad_id: int):
        """Obtener estadísticas de una facultad"""
        response = self.session.get(f"{self.base_url}/estudiantes/estadisticas/facultad/{facultad_id}")
        self._print_response(response)
    
    def health_check(self):
        """Verificar estado de la API"""
        response = self.session.get(f"{self.base_url}/health")
        self._print_response(response)

def print_help():
    """Imprime la ayuda"""
    print("""
🚀 API Client - Practicas ITM

Uso: python api_client.py <comando> [argumentos]

FACULTADES:
  crear-facultad <nombre> [descripcion]    - Crear una facultad
  listar-facultades                        - Listar todas las facultades
  obtener-facultad <id>                    - Obtener una facultad

CARRERAS:
  crear-carrera <nombre> <facultad_id> [desc]  - Crear una carrera
  listar-carreras [facultad_id]                - Listar carreras

ESTUDIANTES:
  crear-estudiante <doc> <nom> <ape> <email> <genero> <fac_id> <car_id> [tel]
  listar-estudiantes [--facultad=id] [--carrera=id] [--estado=str]
  listar-disponibles                       - Listar estudiantes disponibles
  obtener-estudiante <id>                  - Obtener un estudiante
  actualizar-estado <id> <estado>          - Actualizar estado de práctica

ESTADÍSTICAS:
  estadisticas-facultad <id>               - Estadísticas por facultad

SISTEMA:
  health-check                             - Verificar estado de la API
  help                                     - Mostrar esta ayuda

ESTADOS VÁLIDOS:
  Disponible, Contratado, Por Finalizar, Finalizó

GÉNEROS:
  Masculino, Femenino, Otro

EJEMPLO:
  python api_client.py crear-facultad "Ingeniería" "Facultad de Ingeniería"
  python api_client.py listar-facultades
  python api_client.py crear-carrera "Ing. Sistemas" 1 "Carrera de sistemas"
  python api_client.py crear-estudiante "12345678" "Juan" "Pérez" "juan@email.com" "Masculino" 1 1 "3001234567"
  python api_client.py actualizar-estado 1 "Contratado"
    """)

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print_help()
        return
    
    cliente = APIClient()
    comando = sys.argv[1]
    
    try:
        if comando == "health-check":
            cliente.health_check()
        
        elif comando == "crear-facultad":
            if len(sys.argv) < 3:
                print("❌ Error: Uso: crear-facultad <nombre> [descripcion]")
                return
            nombre = sys.argv[2]
            descripcion = sys.argv[3] if len(sys.argv) > 3 else None
            cliente.crear_facultad(nombre, descripcion)
        
        elif comando == "listar-facultades":
            cliente.listar_facultades()
        
        elif comando == "obtener-facultad":
            if len(sys.argv) < 3:
                print("❌ Error: Uso: obtener-facultad <id>")
                return
            cliente.obtener_facultad(int(sys.argv[2]))
        
        elif comando == "crear-carrera":
            if len(sys.argv) < 4:
                print("❌ Error: Uso: crear-carrera <nombre> <facultad_id> [descripcion]")
                return
            nombre = sys.argv[2]
            facultad_id = int(sys.argv[3])
            descripcion = sys.argv[4] if len(sys.argv) > 4 else None
            cliente.crear_carrera(nombre, facultad_id, descripcion)
        
        elif comando == "listar-carreras":
            facultad_id = None
            if len(sys.argv) > 2:
                facultad_id = int(sys.argv[2])
            cliente.listar_carreras(facultad_id)
        
        elif comando == "crear-estudiante":
            if len(sys.argv) < 9:
                print("❌ Error: Uso: crear-estudiante <doc> <nom> <ape> <email> <genero> <fac_id> <car_id> [tel]")
                return
            doc = sys.argv[2]
            nom = sys.argv[3]
            ape = sys.argv[4]
            email = sys.argv[5]
            genero = sys.argv[6]
            fac_id = int(sys.argv[7])
            car_id = int(sys.argv[8])
            tel = sys.argv[9] if len(sys.argv) > 9 else None
            cliente.crear_estudiante(doc, nom, ape, email, genero, fac_id, car_id, tel)
        
        elif comando == "listar-estudiantes":
            fac_id = None
            car_id = None
            estado = None
            for arg in sys.argv[2:]:
                if arg.startswith("--facultad="):
                    fac_id = int(arg.split("=")[1])
                elif arg.startswith("--carrera="):
                    car_id = int(arg.split("=")[1])
                elif arg.startswith("--estado="):
                    estado = arg.split("=")[1]
            cliente.listar_estudiantes(fac_id, car_id, estado)
        
        elif comando == "listar-disponibles":
            cliente.listar_disponibles()
        
        elif comando == "obtener-estudiante":
            if len(sys.argv) < 3:
                print("❌ Error: Uso: obtener-estudiante <id>")
                return
            cliente.obtener_estudiante(int(sys.argv[2]))
        
        elif comando == "actualizar-estado":
            if len(sys.argv) < 4:
                print("❌ Error: Uso: actualizar-estado <id> <estado>")
                return
            estudiante_id = int(sys.argv[2])
            estado = sys.argv[3]
            cliente.actualizar_estado(estudiante_id, estado)
        
        elif comando == "estadisticas-facultad":
            if len(sys.argv) < 3:
                print("❌ Error: Uso: estadisticas-facultad <id>")
                return
            cliente.estadisticas_facultad(int(sys.argv[2]))
        
        elif comando == "help":
            print_help()
        
        else:
            print(f"❌ Comando no reconocido: {comando}")
            print("Usa 'python api_client.py help' para ver los comandos disponibles")
    
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar a la API")
        print("Asegúrate de que el servidor está ejecutándose en http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
