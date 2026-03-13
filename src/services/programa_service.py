"""
Servicio de gestión de Programas Académicos
"""
from sqlalchemy.orm import Session
from src.models.base import Carrera, Facultad
from sqlalchemy import and_, or_

class ProgramaService:
    """Servicio para operaciones CRUD de programas académicos"""
    
    @staticmethod
    def obtener_todos_programas(db: Session, facultad_id: int = None):
        """
        Obtiene todos los programas académicos, opcionalmente filtrados por facultad
        
        Args:
            db: Sesión de base de datos
            facultad_id: ID de facultad (opcional)
            
        Returns:
            List[Carrera]: Lista de programas académicos
        """
        query = db.query(Carrera)
        
        if facultad_id:
            query = query.filter(Carrera.facultad_id == facultad_id)
        
        return query.order_by(Carrera.nombre).all()
    
    @staticmethod
    def obtener_programa_por_id(db: Session, programa_id: int):
        """
        Obtiene un programa académico por ID
        
        Args:
            db: Sesión de base de datos
            programa_id: ID del programa
            
        Returns:
            Carrera: Programa académico o None
        """
        return db.query(Carrera).filter(Carrera.id == programa_id).first()
    
    @staticmethod
    def obtener_programa_por_nombre(db: Session, nombre: str, facultad_id: int = None):
        """
        Obtiene un programa académico por nombre
        
        Args:
            db: Sesión de base de datos
            nombre: Nombre del programa
            facultad_id: ID de facultad (opcional)
            
        Returns:
            Carrera: Programa académico o None
        """
        query = db.query(Carrera).filter(Carrera.nombre == nombre)
        
        if facultad_id:
            query = query.filter(Carrera.facultad_id == facultad_id)
        
        return query.first()
    
    @staticmethod
    def obtener_programas_por_nivel(db: Session, nivel: str):
        """
        Obtiene programas académicos filtrados por nivel
        
        Args:
            db: Sesión de base de datos
            nivel: Nivel (Tecnología, Profesional, Ingeniería)
            
        Returns:
            List[Carrera]: Lista de programas del nivel especificado
        """
        return db.query(Carrera).filter(Carrera.nivel == nivel).order_by(Carrera.nombre).all()
    
    @staticmethod
    def obtener_programas_acreditados(db: Session):
        """
        Obtiene solo programas académicos acreditados
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            List[Carrera]: Lista de programas acreditados
        """
        return db.query(Carrera).filter(Carrera.acreditada == 1).order_by(Carrera.nombre).all()
    
    @staticmethod
    def obtener_programas_virtuales(db: Session):
        """
        Obtiene solo programas académicos virtuales
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            List[Carrera]: Lista de programas virtuales
        """
        return db.query(Carrera).filter(Carrera.virtual == 1).order_by(Carrera.nombre).all()
    
    @staticmethod
    def obtener_estadisticas_programas(db: Session):
        """
        Obtiene estadísticas generales de programas académicos
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            dict: Diccionario con estadísticas
        """
        total_programas = db.query(Carrera).count()
        total_acreditados = db.query(Carrera).filter(Carrera.acreditada == 1).count()
        total_virtuales = db.query(Carrera).filter(Carrera.virtual == 1).count()
        
        # Contar por nivel
        tecnologia = db.query(Carrera).filter(Carrera.nivel == "Tecnología").count()
        profesional = db.query(Carrera).filter(Carrera.nivel == "Profesional").count()
        ingenieria = db.query(Carrera).filter(Carrera.nivel == "Ingeniería").count()
        
        # Contar por facultad
        por_facultad = {}
        facultades = db.query(Facultad).all()
        for facultad in facultades:
            count = db.query(Carrera).filter(Carrera.facultad_id == facultad.id).count()
            if count > 0:
                por_facultad[facultad.nombre] = count
        
        return {
            'total_programas': total_programas,
            'total_acreditados': total_acreditados,
            'total_virtuales': total_virtuales,
            'por_nivel': {
                'Tecnología': tecnologia,
                'Profesional': profesional,
                'Ingeniería': ingenieria
            },
            'por_facultad': por_facultad
        }
    
    @staticmethod
    def crear_programa(db: Session, nombre: str, nivel: str, facultad_id: int, 
                      duracion: str = None, perfil_profesional: str = None,
                      acreditada: bool = False, virtual: bool = False):
        """
        Crea un nuevo programa académico
        
        Args:
            db: Sesión de base de datos
            nombre: Nombre del programa
            nivel: Nivel (Tecnología, Profesional, Ingeniería)
            facultad_id: ID de la facultad
            duracion: Duración del programa
            perfil_profesional: Perfil profesional
            acreditada: Si está acreditado
            virtual: Si es virtual
            
        Returns:
            Carrera: Programa creado
        """
        programa = Carrera(
            nombre=nombre,
            nivel=nivel,
            facultad_id=facultad_id,
            duracion=duracion,
            perfil_profesional=perfil_profesional,
            acreditada=1 if acreditada else 0,
            virtual=1 if virtual else 0
        )
        
        db.add(programa)
        db.commit()
        db.refresh(programa)
        
        return programa
    
    @staticmethod
    def actualizar_programa(db: Session, programa_id: int, **kwargs):
        """
        Actualiza un programa académico
        
        Args:
            db: Sesión de base de datos
            programa_id: ID del programa
            **kwargs: Campos a actualizar
            
        Returns:
            Carrera: Programa actualizado o None
        """
        programa = db.query(Carrera).filter(Carrera.id == programa_id).first()
        
        if not programa:
            return None
        
        # Convertir booleanos a enteros para acreditada y virtual
        if 'acreditada' in kwargs:
            kwargs['acreditada'] = 1 if kwargs['acreditada'] else 0
        if 'virtual' in kwargs:
            kwargs['virtual'] = 1 if kwargs['virtual'] else 0
        
        for key, value in kwargs.items():
            if hasattr(programa, key):
                setattr(programa, key, value)
        
        db.commit()
        db.refresh(programa)
        
        return programa
    
    @staticmethod
    def eliminar_programa(db: Session, programa_id: int) -> bool:
        """
        Elimina un programa académico
        
        Args:
            db: Sesión de base de datos
            programa_id: ID del programa
            
        Returns:
            bool: True si se eliminó, False si no existe
        """
        programa = db.query(Carrera).filter(Carrera.id == programa_id).first()
        
        if not programa:
            return False
        
        db.delete(programa)
        db.commit()
        
        return True
