"""
Servicio para gestión de CVs en EFS
"""
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from src.config import get_config


class CVService:

    @staticmethod
    def upload_cv(estudiante_id: int, file_bytes: bytes, original_filename: str) -> str:
        """
        Guarda el CV en EFS y retorna la ruta relativa.
        Reemplaza el CV anterior si existe.
        """
        config = get_config()

        if len(file_bytes) > config.CV_MAX_SIZE_MB * 1024 * 1024:
            raise ValueError(f"El archivo supera el límite de {config.CV_MAX_SIZE_MB} MB")

        safe_name = secure_filename(original_filename)
        if not safe_name.lower().endswith('.pdf'):
            raise ValueError("Solo se permiten archivos PDF")

        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        relative_path = os.path.join(str(estudiante_id), f"{timestamp}_{safe_name}")
        abs_path = os.path.join(config.EFS_CV_PATH, relative_path)

        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, 'wb') as f:
            f.write(file_bytes)

        return relative_path

    @staticmethod
    def get_file_path(relative_path: str) -> str:
        """Retorna la ruta absoluta del CV en EFS."""
        config = get_config()
        abs_path = os.path.join(config.EFS_CV_PATH, relative_path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError("Archivo CV no encontrado en EFS")
        return abs_path

    @staticmethod
    def delete_cv(relative_path: str) -> bool:
        """Elimina el CV del EFS."""
        try:
            config = get_config()
            abs_path = os.path.join(config.EFS_CV_PATH, relative_path)
            if os.path.exists(abs_path):
                os.remove(abs_path)
            return True
        except OSError:
            return False
