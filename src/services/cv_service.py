"""
Servicio para gestión de CVs en S3
"""
import os
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from werkzeug.utils import secure_filename
from src.config import get_config


def _get_s3_client():
    config = get_config()
    return boto3.client('s3', region_name=config.S3_REGION)


def _get_bucket():
    config = get_config()
    bucket = config.S3_CV_BUCKET
    if not bucket:
        raise ValueError("S3_CV_BUCKET no está configurado")
    return bucket


class CVService:

    @staticmethod
    def upload_cv(estudiante_id: int, file_bytes: bytes, original_filename: str) -> str:
        """
        Sube el CV a S3 y retorna el s3_key.
        Reemplaza el CV anterior si existe.
        """
        config = get_config()

        if len(file_bytes) > config.CV_MAX_SIZE_MB * 1024 * 1024:
            raise ValueError(f"El archivo supera el límite de {config.CV_MAX_SIZE_MB} MB")

        safe_name = secure_filename(original_filename)
        if not safe_name.lower().endswith('.pdf'):
            raise ValueError("Solo se permiten archivos PDF")

        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        s3_key = f"cvs/{estudiante_id}/{timestamp}_{safe_name}"

        bucket = _get_bucket()
        s3 = _get_s3_client()
        s3.put_object(
            Bucket=bucket,
            Key=s3_key,
            Body=file_bytes,
            ContentType='application/pdf',
            ContentDisposition=f'inline; filename="{safe_name}"',
        )
        return s3_key

    @staticmethod
    def get_presigned_url(s3_key: str, expiration: int = 3600) -> str:
        """Genera una URL prefirmada para descargar/visualizar el CV."""
        bucket = _get_bucket()
        s3 = _get_s3_client()
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': s3_key},
            ExpiresIn=expiration,
        )
        return url

    @staticmethod
    def delete_cv(s3_key: str) -> bool:
        """Elimina el CV de S3."""
        try:
            bucket = _get_bucket()
            s3 = _get_s3_client()
            s3.delete_object(Bucket=bucket, Key=s3_key)
            return True
        except ClientError:
            return False
