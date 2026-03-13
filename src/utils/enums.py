"""
Enumeraciones para el módulo de prácticas
"""
from enum import Enum

class EstadoPractica(Enum):
    """Estados posibles de una práctica"""
    DISPONIBLE = "Disponible"
    CONTRATADO = "Contratado"
    POR_FINALIZAR = "Por Finalizar"
    FINALIZO = "Finalizó"
    
    def __str__(self):
        return self.value

class Genero(Enum):
    """Géneros"""
    MASCULINO = "Masculino"
    FEMENINO = "Femenino"
    OTRO = "Otro"
    
    def __str__(self):
        return self.value
