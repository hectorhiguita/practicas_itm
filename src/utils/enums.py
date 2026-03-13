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
    """Géneros - Opciones inclusivas"""
    MASCULINO = "Masculino"
    FEMENINO = "Femenino"
    NO_BINARIO = "No Binario"
    TRANSGENDER_MASCULINO = "Hombre Transgénero"
    TRANSGENDER_FEMENINO = "Mujer Transgénero"
    GENDERQUEER = "Genderqueer"
    ASEXUAL = "Asexual"
    OTRO = "Otro"
    PREFIERO_NO_DECIR = "Prefiero no decir"
    
    def __str__(self):
        return self.value
