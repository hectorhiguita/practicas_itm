"""
Modelos de base de datos para la aplicación
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from src.utils.enums import EstadoPractica, Genero

Base = declarative_base()

class Facultad(Base):
    """Modelo de Facultad"""
    __tablename__ = 'facultades'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(255), unique=True, nullable=False)
    descripcion = Column(String(500))
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    carreras = relationship("Carrera", back_populates="facultad", cascade="all, delete-orphan")
    estudiantes = relationship("Estudiante", back_populates="facultad", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Facultad(id={self.id}, nombre='{self.nombre}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }

class Carrera(Base):
    """Modelo de Carrera/Programa Académico"""
    __tablename__ = 'carreras'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(String(500))
    nivel = Column(String(100), nullable=False)  # Tecnología, Profesional, Ingeniería
    duracion = Column(String(50), nullable=True)  # Ej: 6 semestres, 10 semestres
    perfil_profesional = Column(String(1000), nullable=True)
    acreditada = Column(Integer, default=0, nullable=False)  # 0=NO, 1=SI
    virtual = Column(Integer, default=0, nullable=False)  # 0=NO, 1=SI
    facultad_id = Column(Integer, ForeignKey('facultades.id'), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    facultad = relationship("Facultad", back_populates="carreras")
    estudiantes = relationship("Estudiante", back_populates="carrera", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Carrera(id={self.id}, nombre='{self.nombre}', nivel='{self.nivel}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'nivel': self.nivel,
            'duracion': self.duracion,
            'perfil_profesional': self.perfil_profesional,
            'acreditada': bool(self.acreditada),
            'virtual': bool(self.virtual),
            'facultad_id': self.facultad_id,
            'facultad_nombre': self.facultad.nombre if self.facultad else None,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }

class Estudiante(Base):
    """Modelo de Estudiante"""
    __tablename__ = 'estudiantes'
    
    id = Column(Integer, primary_key=True)
    numero_documento = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(255), nullable=False)
    apellido = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    telefono = Column(String(20))
    genero = Column(SQLEnum(Genero), nullable=False)
    tiene_discapacidad = Column(String(255), nullable=True)
    discapacidad_personalizada = Column(String(500), nullable=True)
    estado_practica = Column(SQLEnum(EstadoPractica), default=EstadoPractica.DISPONIBLE, nullable=False)
    facultad_id = Column(Integer, ForeignKey('facultades.id'), nullable=False)
    carrera_id = Column(Integer, ForeignKey('carreras.id'), nullable=False)
    # CV
    cv_s3_key = Column(String(500), nullable=True)
    cv_filename = Column(String(255), nullable=True)
    cv_upload_date = Column(DateTime, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    facultad = relationship("Facultad", back_populates="estudiantes")
    carrera = relationship("Carrera", back_populates="estudiantes")
    
    def __repr__(self):
        return f"<Estudiante(id={self.id}, nombre='{self.nombre}', documento='{self.numero_documento}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero_documento': self.numero_documento,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'email': self.email,
            'telefono': self.telefono,
            'genero': self.genero.value if self.genero else None,
            'tiene_discapacidad': self.tiene_discapacidad,
            'discapacidad_personalizada': self.discapacidad_personalizada,
            'estado_practica': self.estado_practica.value if self.estado_practica else None,
            'facultad_id': self.facultad_id,
            'carrera_id': self.carrera_id,
            'cv_filename': self.cv_filename,
            'cv_upload_date': self.cv_upload_date.isoformat() if self.cv_upload_date else None,
            'tiene_cv': self.cv_s3_key is not None,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }
