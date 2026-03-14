"""
Servicio para gestión de Asesores de Prácticas
"""
from sqlalchemy.orm import Session
from src.models.base import Asesor, Estudiante
from src.utils.enums import EstadoPractica


ESTADO_ACTIVO = {
    EstadoPractica.DISPONIBLE,
    EstadoPractica.EN_PROCESO,
    EstadoPractica.CONTRATADO,
    EstadoPractica.POR_FINALIZAR,
}


class AsesorService:

    @staticmethod
    def listar_asesores(db: Session, solo_activos: bool = False):
        q = db.query(Asesor)
        if solo_activos:
            q = q.filter(Asesor.activo == True)
        return q.order_by(Asesor.apellido, Asesor.nombre).all()

    @staticmethod
    def obtener_asesor(db: Session, asesor_id: int):
        return db.query(Asesor).filter(Asesor.id == asesor_id).first()

    @staticmethod
    def crear_asesor(db: Session, datos: dict) -> Asesor:
        asesor = Asesor(
            nombre=datos['nombre'].strip(),
            apellido=datos['apellido'].strip(),
            email=datos['email'].strip().lower(),
            telefono=datos.get('telefono', '').strip() or None,
        )
        db.add(asesor)
        db.commit()
        db.refresh(asesor)
        return asesor

    @staticmethod
    def actualizar_asesor(db: Session, asesor_id: int, datos: dict) -> Asesor:
        asesor = AsesorService.obtener_asesor(db, asesor_id)
        if not asesor:
            return None
        for campo in ('nombre', 'apellido', 'email', 'telefono', 'activo'):
            if campo in datos:
                val = datos[campo]
                if isinstance(val, str):
                    val = val.strip() or None
                setattr(asesor, campo, val)
        db.commit()
        db.refresh(asesor)
        return asesor

    @staticmethod
    def eliminar_asesor(db: Session, asesor_id: int) -> bool:
        """Desactiva el asesor (no borra para preservar histórico)."""
        asesor = AsesorService.obtener_asesor(db, asesor_id)
        if not asesor:
            return False
        asesor.activo = False
        db.commit()
        return True

    @staticmethod
    def get_estadisticas(db: Session, asesor_id: int) -> dict:
        """
        Retorna conteo de estudiantes por estado para un asesor.
        Activos: todos los estados excepto FINALIZADO.
        Histórico: todos (incluye finalizados).
        """
        estudiantes = db.query(Estudiante).filter(
            Estudiante.asesor_id == asesor_id
        ).all()

        por_estado = {}
        activos = 0
        for est in estudiantes:
            estado = est.estado_practica.value if est.estado_practica else 'Desconocido'
            por_estado[estado] = por_estado.get(estado, 0) + 1
            if est.estado_practica in ESTADO_ACTIVO:
                activos += 1

        return {
            'total_historico': len(estudiantes),
            'total_activos': activos,
            'por_estado': por_estado,
        }

    @staticmethod
    def get_dashboard(db: Session) -> list:
        """
        Retorna todos los asesores con sus estadísticas para el dashboard.
        """
        asesores = AsesorService.listar_asesores(db, solo_activos=False)
        result = []
        for asesor in asesores:
            d = asesor.to_dict()
            d['estadisticas'] = AsesorService.get_estadisticas(db, asesor.id)
            result.append(d)
        return result

    @staticmethod
    def get_estudiantes_asesor(db: Session, asesor_id: int, incluir_finalizados: bool = True) -> list:
        """Retorna los estudiantes de un asesor."""
        q = db.query(Estudiante).filter(Estudiante.asesor_id == asesor_id)
        if not incluir_finalizados:
            q = q.filter(Estudiante.estado_practica.in_(list(ESTADO_ACTIVO)))
        return q.order_by(Estudiante.apellido, Estudiante.nombre).all()

    @staticmethod
    def asignar_asesor(db: Session, estudiante_id: int, asesor_id: int) -> Estudiante:
        """Asigna (o cambia) el asesor de un estudiante."""
        estudiante = db.query(Estudiante).filter(Estudiante.id == estudiante_id).first()
        if not estudiante:
            return None
        if asesor_id:
            asesor = AsesorService.obtener_asesor(db, asesor_id)
            if not asesor:
                return None
        estudiante.asesor_id = asesor_id or None
        db.commit()
        db.refresh(estudiante)
        return estudiante
