"""
Servicio de lógica de negocio para Estudiantes
"""
from sqlalchemy.orm import Session
from src.models.base import Estudiante, Facultad, Carrera
from src.utils.enums import EstadoPractica, Genero
from typing import List, Optional

class EstudianteService:
    """Servicio para gestionar estudiantes"""
    
    @staticmethod
    def crear_estudiante(db: Session, numero_documento: str, nombre: str, apellido: str,
                        email: str, genero: str, facultad_id: int, carrera_id: int,
                        telefono: str = None) -> Estudiante:
        """
        Crea un nuevo estudiante
        
        Args:
            db: Sesión de base de datos
            numero_documento: Número de documento único
            nombre: Nombre del estudiante
            apellido: Apellido del estudiante
            email: Email del estudiante
            genero: Género (Masculino, Femenino, Otro)
            facultad_id: ID de la facultad
            carrera_id: ID de la carrera
            telefono: Teléfono opcional
            
        Returns:
            Estudiante: El estudiante creado
            
        Raises:
            ValueError: Si hay datos inválidos o duplicados
        """
        # Validar que no exista estudiante con mismo documento
        estudiante_existente = db.query(Estudiante).filter(
            Estudiante.numero_documento == numero_documento
        ).first()
        if estudiante_existente:
            raise ValueError(f"Ya existe un estudiante con documento '{numero_documento}'")
        
        # Validar que no exista estudiante con mismo email
        email_existente = db.query(Estudiante).filter(Estudiante.email == email).first()
        if email_existente:
            raise ValueError(f"El email '{email}' ya está registrado")
        
        # Validar que existan facultad y carrera
        facultad = db.query(Facultad).filter(Facultad.id == facultad_id).first()
        if not facultad:
            raise ValueError(f"La facultad con ID {facultad_id} no existe")
        
        carrera = db.query(Carrera).filter(Carrera.id == carrera_id).first()
        if not carrera:
            raise ValueError(f"La carrera con ID {carrera_id} no existe")
        
        # Validar género
        try:
            genero_enum = Genero[genero.upper()] if isinstance(genero, str) else genero
        except (KeyError, AttributeError):
            raise ValueError(f"Género inválido: {genero}")
        
        estudiante = Estudiante(
            numero_documento=numero_documento,
            nombre=nombre,
            apellido=apellido,
            email=email,
            genero=genero_enum,
            facultad_id=facultad_id,
            carrera_id=carrera_id,
            telefono=telefono,
            estado_practica=EstadoPractica.DISPONIBLE
        )
        db.add(estudiante)
        db.commit()
        db.refresh(estudiante)
        return estudiante
    
    @staticmethod
    def obtener_estudiante(db: Session, estudiante_id: int) -> Optional[Estudiante]:
        """
        Obtiene un estudiante por ID
        
        Args:
            db: Sesión de base de datos
            estudiante_id: ID del estudiante
            
        Returns:
            Estudiante o None si no existe
        """
        return db.query(Estudiante).filter(Estudiante.id == estudiante_id).first()
    
    @staticmethod
    def obtener_estudiante_por_documento(db: Session, numero_documento: str) -> Optional[Estudiante]:
        """
        Obtiene un estudiante por número de documento
        
        Args:
            db: Sesión de base de datos
            numero_documento: Número de documento
            
        Returns:
            Estudiante o None si no existe
        """
        return db.query(Estudiante).filter(
            Estudiante.numero_documento == numero_documento
        ).first()
    
    @staticmethod
    def obtener_estudiante_por_email(db: Session, email: str) -> Optional[Estudiante]:
        """
        Obtiene un estudiante por email
        
        Args:
            db: Sesión de base de datos
            email: Email del estudiante
            
        Returns:
            Estudiante o None si no existe
        """
        return db.query(Estudiante).filter(Estudiante.email == email).first()
    
    @staticmethod
    def obtener_todos_estudiantes(db: Session) -> List[Estudiante]:
        """
        Obtiene todos los estudiantes
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            Lista de estudiantes
        """
        return db.query(Estudiante).all()
    
    @staticmethod
    def obtener_estudiantes_por_facultad(db: Session, facultad_id: int) -> List[Estudiante]:
        """
        Obtiene todos los estudiantes de una facultad
        
        Args:
            db: Sesión de base de datos
            facultad_id: ID de la facultad
            
        Returns:
            Lista de estudiantes
        """
        return db.query(Estudiante).filter(Estudiante.facultad_id == facultad_id).all()
    
    @staticmethod
    def obtener_estudiantes_por_carrera(db: Session, carrera_id: int) -> List[Estudiante]:
        """
        Obtiene todos los estudiantes de una carrera
        
        Args:
            db: Sesión de base de datos
            carrera_id: ID de la carrera
            
        Returns:
            Lista de estudiantes
        """
        return db.query(Estudiante).filter(Estudiante.carrera_id == carrera_id).all()
    
    @staticmethod
    def obtener_estudiantes_por_estado(db: Session, estado: str) -> List[Estudiante]:
        """
        Obtiene estudiantes por estado de práctica
        
        Args:
            db: Sesión de base de datos
            estado: Estado de práctica (Disponible, Contratado, etc)
            
        Returns:
            Lista de estudiantes
            
        Raises:
            ValueError: Si el estado es inválido
        """
        try:
            estado_enum = EstadoPractica[estado.upper()] if isinstance(estado, str) else estado
        except (KeyError, AttributeError):
            raise ValueError(f"Estado inválido: {estado}")
        
        return db.query(Estudiante).filter(Estudiante.estado_practica == estado_enum).all()
    
    @staticmethod
    def obtener_estudiantes_disponibles(db: Session) -> List[Estudiante]:
        """
        Obtiene todos los estudiantes disponibles para prácticas
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            Lista de estudiantes disponibles
        """
        return EstudianteService.obtener_estudiantes_por_estado(db, "disponible")
    
    @staticmethod
    def actualizar_estado_practica(db: Session, estudiante_id: int, nuevo_estado: str, fecha_inicio_contrato: str = None, fecha_fin_contrato: str = None) -> Optional[Estudiante]:
        """
        Actualiza el estado de práctica de un estudiante
        
        Args:
            db: Sesión de base de datos
            estudiante_id: ID del estudiante
            nuevo_estado: Nuevo estado (Disponible, Contratado, Por Finalizar, Finalizó)
            
        Returns:
            Estudiante actualizado o None si no existe
            
        Raises:
            ValueError: Si el estado es inválido
        """
        estudiante = EstudianteService.obtener_estudiante(db, estudiante_id)
        if not estudiante:
            return None
        
        try:
            # Convertir el estado a enum
            # Primero intentamos buscar por valor directo
            estado_enum = None
            if isinstance(nuevo_estado, str):
                for estado in EstadoPractica:
                    if estado.value == nuevo_estado:
                        estado_enum = estado
                        break
                
                if not estado_enum:
                    raise ValueError(f"Estado inválido: {nuevo_estado}")
            else:
                estado_enum = nuevo_estado
        except (KeyError, AttributeError):
            raise ValueError(f"Estado inválido: {nuevo_estado}")
        
        estudiante.estado_practica = estado_enum
        if estado_enum.value == 'Contratado':
            from datetime import datetime as dt
            import calendar
            if fecha_inicio_contrato:
                inicio = dt.fromisoformat(fecha_inicio_contrato)
                estudiante.fecha_inicio_contrato = inicio
            else:
                from datetime import timezone
                inicio = estudiante.fecha_inicio_contrato or dt.now(timezone.utc).replace(tzinfo=None)

            if fecha_fin_contrato:
                estudiante.fecha_fin_contrato = dt.fromisoformat(fecha_fin_contrato)
            elif not estudiante.fecha_fin_contrato:
                # Por defecto 6 meses desde el inicio
                m = inicio.month - 1 + 6
                year = inicio.year + m // 12
                month = m % 12 + 1
                day = min(inicio.day, calendar.monthrange(year, month)[1])
                estudiante.fecha_fin_contrato = inicio.replace(year=year, month=month, day=day)
        db.commit()
        db.refresh(estudiante)
        return estudiante

    @staticmethod
    def actualizar_estados_por_vencimiento(db: Session) -> int:
        """
        Cambia a 'Por Finalizar' a todos los estudiantes 'Contratado' cuyo
        fecha_fin_contrato es en 30 días o menos.
        Retorna la cantidad de estudiantes actualizados.
        """
        from datetime import datetime as dt, timedelta, timezone
        ahora = dt.now(timezone.utc).replace(tzinfo=None)
        limite = ahora + timedelta(days=30)

        estudiantes = db.query(Estudiante).filter(
            Estudiante.estado_practica == EstadoPractica.CONTRATADO,
            Estudiante.fecha_fin_contrato != None,
            Estudiante.fecha_fin_contrato <= limite
        ).all()

        for est in estudiantes:
            est.estado_practica = EstadoPractica.POR_FINALIZAR

        if estudiantes:
            db.commit()

        return len(estudiantes)

    @staticmethod
    def actualizar_estudiante(db: Session, estudiante_id: int, nombre: str = None,
                             apellido: str = None, email: str = None,
                             telefono: str = None, genero: str = None,
                             facultad_id: int = None, carrera_id: int = None,
                             estado_practica: str = None,
                             tiene_discapacidad: str = None,
                             discapacidad_personalizada: str = None,
                             fecha_inicio_contrato: str = None,
                             fecha_fin_contrato: str = None) -> Optional[Estudiante]:
        """
        Actualiza datos de un estudiante

        Args:
            db: Sesión de base de datos
            estudiante_id: ID del estudiante
            nombre, apellido, email, telefono, genero: Datos personales (opcionales)
            facultad_id, carrera_id: Asignación académica (opcionales)
            estado_practica: Nuevo estado (opcional)
            tiene_discapacidad, discapacidad_personalizada: Datos de discapacidad (opcionales)

        Returns:
            Estudiante actualizado o None si no existe
        """
        estudiante = EstudianteService.obtener_estudiante(db, estudiante_id)
        if not estudiante:
            return None

        if nombre:
            estudiante.nombre = nombre
        if apellido:
            estudiante.apellido = apellido
        if email:
            email_existente = db.query(Estudiante).filter(
                Estudiante.email == email,
                Estudiante.id != estudiante_id
            ).first()
            if email_existente:
                raise ValueError(f"El email '{email}' ya está registrado")
            estudiante.email = email
        if telefono:
            estudiante.telefono = telefono

        if genero:
            try:
                genero_enum = Genero[genero.upper()] if isinstance(genero, str) else genero
            except (KeyError, AttributeError):
                raise ValueError(f"Género inválido: {genero}")
            estudiante.genero = genero_enum

        if facultad_id:
            facultad = db.query(Facultad).filter(Facultad.id == facultad_id).first()
            if not facultad:
                raise ValueError(f"La facultad con ID {facultad_id} no existe")
            estudiante.facultad_id = facultad_id

        if carrera_id:
            carrera = db.query(Carrera).filter(Carrera.id == carrera_id).first()
            if not carrera:
                raise ValueError(f"La carrera con ID {carrera_id} no existe")
            estudiante.carrera_id = carrera_id

        if estado_practica:
            estado_enum = None
            for estado in EstadoPractica:
                if estado.value == estado_practica:
                    estado_enum = estado
                    break
            if not estado_enum:
                raise ValueError(f"Estado inválido: {estado_practica}")
            estudiante.estado_practica = estado_enum

        # tiene_discapacidad puede ser cadena vacía (sin discapacidad), por eso se usa `is not None`
        if tiene_discapacidad is not None:
            estudiante.tiene_discapacidad = tiene_discapacidad or None

        if discapacidad_personalizada is not None:
            estudiante.discapacidad_personalizada = discapacidad_personalizada or None

        if fecha_inicio_contrato:
            from datetime import datetime as dt
            estudiante.fecha_inicio_contrato = dt.fromisoformat(fecha_inicio_contrato)

        if fecha_fin_contrato:
            from datetime import datetime as dt
            estudiante.fecha_fin_contrato = dt.fromisoformat(fecha_fin_contrato)

        db.commit()
        db.refresh(estudiante)
        return estudiante
    
    @staticmethod
    def eliminar_estudiante(db: Session, estudiante_id: int) -> bool:
        """
        Elimina un estudiante
        
        Args:
            db: Sesión de base de datos
            estudiante_id: ID del estudiante
            
        Returns:
            True si se eliminó exitosamente
        """
        estudiante = EstudianteService.obtener_estudiante(db, estudiante_id)
        if not estudiante:
            return False
        
        db.delete(estudiante)
        db.commit()
        return True
    
    @staticmethod
    def obtener_estadisticas_facultad(db: Session, facultad_id: int) -> dict:
        """
        Obtiene estadísticas de estudiantes por estado en una facultad
        
        Args:
            db: Sesión de base de datos
            facultad_id: ID de la facultad
            
        Returns:
            Diccionario con estadísticas
        """
        estudiantes = EstudianteService.obtener_estudiantes_por_facultad(db, facultad_id)
        
        estadisticas = {
            'total': len(estudiantes),
            'disponible': len([e for e in estudiantes if e.estado_practica == EstadoPractica.DISPONIBLE]),
            'contratado': len([e for e in estudiantes if e.estado_practica == EstadoPractica.CONTRATADO]),
            'por_finalizar': len([e for e in estudiantes if e.estado_practica == EstadoPractica.POR_FINALIZAR]),
            'finalizo': len([e for e in estudiantes if e.estado_practica == EstadoPractica.FINALIZO])
        }
        
        return estadisticas
    
    @staticmethod
    def obtener_estadisticas_carrera(db: Session, carrera_id: int) -> dict:
        """
        Obtiene estadísticas de estudiantes por estado en una carrera
        
        Args:
            db: Sesión de base de datos
            carrera_id: ID de la carrera
            
        Returns:
            Diccionario con estadísticas
        """
        estudiantes = EstudianteService.obtener_estudiantes_por_carrera(db, carrera_id)
        
        estadisticas = {
            'total': len(estudiantes),
            'disponible': len([e for e in estudiantes if e.estado_practica == EstadoPractica.DISPONIBLE]),
            'contratado': len([e for e in estudiantes if e.estado_practica == EstadoPractica.CONTRATADO]),
            'por_finalizar': len([e for e in estudiantes if e.estado_practica == EstadoPractica.POR_FINALIZAR]),
            'finalizo': len([e for e in estudiantes if e.estado_practica == EstadoPractica.FINALIZO])
        }
        
        return estadisticas
