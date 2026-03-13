"""
Servicio de lógica de negocio para Carreras
"""
from sqlalchemy.orm import Session
from src.models.base import Carrera, Facultad
from typing import List, Optional

class CarreraService:
    """Servicio para gestionar carreras"""
    
    @staticmethod
    def crear_carrera(db: Session, nombre: str, facultad_id: int, descripcion: str = None,
                      nivel: str = 'Tecnología', duracion: str = None,
                      perfil_profesional: str = None, acreditada: bool = False,
                      virtual: bool = False) -> Carrera:
        """
        Crea una nueva carrera

        Args:
            db: Sesión de base de datos
            nombre: Nombre de la carrera
            facultad_id: ID de la facultad a la que pertenece
            descripcion: Descripción opcional de la carrera
            nivel: Nivel académico (Tecnología, Profesional, Ingeniería)
            duracion: Duración del programa
            perfil_profesional: Perfil profesional del egresado
            acreditada: Si el programa está acreditado
            virtual: Si el programa es virtual

        Returns:
            Carrera: La carrera creada

        Raises:
            ValueError: Si la facultad no existe
        """
        facultad = db.query(Facultad).filter(Facultad.id == facultad_id).first()
        if not facultad:
            raise ValueError(f"La facultad con ID {facultad_id} no existe")

        carrera = Carrera(
            nombre=nombre,
            facultad_id=facultad_id,
            descripcion=descripcion,
            nivel=nivel,
            duracion=duracion,
            perfil_profesional=perfil_profesional,
            acreditada=1 if acreditada else 0,
            virtual=1 if virtual else 0,
        )
        db.add(carrera)
        db.commit()
        db.refresh(carrera)
        return carrera
    
    @staticmethod
    def obtener_carrera(db: Session, carrera_id: int) -> Optional[Carrera]:
        """
        Obtiene una carrera por ID
        
        Args:
            db: Sesión de base de datos
            carrera_id: ID de la carrera
            
        Returns:
            Carrera o None si no existe
        """
        return db.query(Carrera).filter(Carrera.id == carrera_id).first()
    
    @staticmethod
    def obtener_carreras_por_facultad(db: Session, facultad_id: int) -> List[Carrera]:
        """
        Obtiene todas las carreras de una facultad
        
        Args:
            db: Sesión de base de datos
            facultad_id: ID de la facultad
            
        Returns:
            Lista de carreras
        """
        return db.query(Carrera).filter(Carrera.facultad_id == facultad_id).all()
    
    @staticmethod
    def obtener_todas_carreras(db: Session) -> List[Carrera]:
        """
        Obtiene todas las carreras
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            Lista de carreras
        """
        return db.query(Carrera).all()
    
    @staticmethod
    def actualizar_carrera(db: Session, carrera_id: int, nombre: str = None,
                          descripcion: str = None) -> Optional[Carrera]:
        """
        Actualiza una carrera
        
        Args:
            db: Sesión de base de datos
            carrera_id: ID de la carrera
            nombre: Nuevo nombre (opcional)
            descripcion: Nueva descripción (opcional)
            
        Returns:
            Carrera actualizada o None si no existe
        """
        carrera = CarreraService.obtener_carrera(db, carrera_id)
        if not carrera:
            return None
        
        if nombre:
            carrera.nombre = nombre
        if descripcion:
            carrera.descripcion = descripcion
        
        db.commit()
        db.refresh(carrera)
        return carrera
    
    @staticmethod
    def eliminar_carrera(db: Session, carrera_id: int) -> bool:
        """
        Elimina una carrera
        
        Args:
            db: Sesión de base de datos
            carrera_id: ID de la carrera
            
        Returns:
            True si se eliminó exitosamente
        """
        carrera = CarreraService.obtener_carrera(db, carrera_id)
        if not carrera:
            return False
        
        db.delete(carrera)
        db.commit()
        return True
