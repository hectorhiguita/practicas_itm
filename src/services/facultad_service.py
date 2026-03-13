"""
Servicio de lógica de negocio para Facultades
"""
from sqlalchemy.orm import Session
from src.models.base import Facultad
from typing import List, Optional

class FacultadService:
    """Servicio para gestionar facultades"""
    
    @staticmethod
    def crear_facultad(db: Session, nombre: str, descripcion: str = None) -> Facultad:
        """
        Crea una nueva facultad
        
        Args:
            db: Sesión de base de datos
            nombre: Nombre de la facultad
            descripcion: Descripción opcional de la facultad
            
        Returns:
            Facultad: La facultad creada
            
        Raises:
            ValueError: Si la facultad ya existe
        """
        # Verificar que no exista
        facultad_existente = db.query(Facultad).filter(Facultad.nombre == nombre).first()
        if facultad_existente:
            raise ValueError(f"La facultad '{nombre}' ya existe")
        
        facultad = Facultad(nombre=nombre, descripcion=descripcion)
        db.add(facultad)
        db.commit()
        db.refresh(facultad)
        return facultad
    
    @staticmethod
    def obtener_facultad(db: Session, facultad_id: int) -> Optional[Facultad]:
        """
        Obtiene una facultad por ID
        
        Args:
            db: Sesión de base de datos
            facultad_id: ID de la facultad
            
        Returns:
            Facultad o None si no existe
        """
        return db.query(Facultad).filter(Facultad.id == facultad_id).first()
    
    @staticmethod
    def obtener_todas_facultades(db: Session) -> List[Facultad]:
        """
        Obtiene todas las facultades
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            Lista de facultades
        """
        return db.query(Facultad).all()
    
    @staticmethod
    def actualizar_facultad(db: Session, facultad_id: int, nombre: str = None, 
                           descripcion: str = None) -> Optional[Facultad]:
        """
        Actualiza una facultad
        
        Args:
            db: Sesión de base de datos
            facultad_id: ID de la facultad
            nombre: Nuevo nombre (opcional)
            descripcion: Nueva descripción (opcional)
            
        Returns:
            Facultad actualizada o None si no existe
        """
        facultad = FacultadService.obtener_facultad(db, facultad_id)
        if not facultad:
            return None
        
        if nombre:
            facultad.nombre = nombre
        if descripcion:
            facultad.descripcion = descripcion
        
        db.commit()
        db.refresh(facultad)
        return facultad
    
    @staticmethod
    def eliminar_facultad(db: Session, facultad_id: int) -> bool:
        """
        Elimina una facultad
        
        Args:
            db: Sesión de base de datos
            facultad_id: ID de la facultad
            
        Returns:
            True si se eliminó exitosamente
        """
        facultad = FacultadService.obtener_facultad(db, facultad_id)
        if not facultad:
            return False
        
        db.delete(facultad)
        db.commit()
        return True
