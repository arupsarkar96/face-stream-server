from minio import Minio

from app.core.config import settings

minio_client = Minio(
        endpoint=settings.S3_HOST,
        access_key=settings.S3_ACCESS_KEY,
        secret_key=settings.S3_SECRET_KEY,
        secure=False
)